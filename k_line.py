# -*-coding=utf-8-*-
# 获取 不同形态的k线
import random
import time
import tushare as ts
import pandas as pd
import os, datetime, math
import numpy as np
import logging
from setting import get_engine, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, REDIS_HOST, get_mysql_conn
import redis
from threading import Thread
import MySQLdb
from collect_data import SaveData
engine = get_engine('history')
conn = ts.get_apis()
MYSQL_DB = 'history'
cursor = get_mysql_conn(MYSQL_DB).cursor()


# pd.set_option('display.max_rows', None)

class Kline():
    def __init__(self):
        logging.info('tushare version: {}'.format(ts.__version__))
        path = os.path.join(os.getcwd(), 'data')
        self.today_date = datetime.datetime.now().strftime('%Y-%m-%d')
        logging.info(self.today_date)
        if not os.path.exists(path):
            os.mkdir(path)
        os.chdir(path)
        # self.conn=ts.get_apis()

    def store_base_data(self, target):
        self.all_info = ts.get_stock_basics()
        self.all_info = self.all_info.reset_index()
        print self.all_info
        if target == 'sql':
            self.all_info.to_sql('tb_baseinfo', engine,if_exists='replace')

        elif target == 'csv':
            self.all_info.to_csv('baseInfo.csv')
        else:
            logging.info('sql or csv option. Not get right argument')

    # 枚举每一个股票代码
    def store_hist_data(self):
        read_cmd = 'select * from tb_baseInfo;'
        df = pd.read_sql(read_cmd, engine)
        for i in range(len(df)):
            code, name, start_date = df.loc[i]['code'], df.loc[i]['name'], df.loc[i]['timeToMarket']
            self.get_hist_data(code, name, start_date)
            # time.sleep(random.random())
            print code, name, start_date

    # 获取历史行情，前复权 ，使用bar函数，get_hist_data 经常会出错
    def get_hist_data(self, code, name, start_data):
        try:
            start_data = datetime.datetime.strptime(str(start_data), '%Y%m%d').strftime('%Y-%m-%d')
            df = ts.bar(code, conn=conn, start_date=start_data, adj='qfq')
            print df
        except Exception, e:
            print e
            return

        df.insert(1, 'name', name)
        df = df.reset_index()
        try:
            df.to_sql(code, engine, if_exists='append')
        except Exception, e:
            print e

    def inital_data(self, target):
        if target == 'sql':
            self.today = pd.read_csv(self.today_date + '.csv', dtype={'code': np.str})
            self.all = pd.read_csv('bases.csv', dtype={'code': np.str})

    def _xiayingxian(self, row, ratio):
        '''
        下影线的逻辑 ratio 下影线的长度比例，数字越大，下影线越长
        row: series类型
        '''
        open_p = float(row['open'])
        # print open_p
        closed = float(row['close'])
        # print closed
        low = float(row['low'])
        # print low
        high = float(row['high'])
        p = min(closed,open_p)
        try:
            diff = (p - low) * 1.00 / (high - low)
            diff=round(diff,3)
        except ZeroDivisionError:
            diff = 0
        if diff > ratio:
                xiayinxian_engine = get_engine('db_selection')
                date,code,name,ocupy_ration ,standards = row['datetime'],row['code'],row['name'],diff,ratio
                df = pd.DataFrame(
                    {'datetime': [date], 'code': [code], 'name': [name], 'ocupy_ration': [ocupy_ration],
                     'standards': [standards]})
                try:
                    df1=pd.read_sql_table('xiayingxian',xiayinxian_engine,index_col='index')
                    df = pd.concat([df1, df])
                except Exception,e:
                    print e
                    #return None

                df = df.reset_index(drop=True)
                df.to_sql('xiayingxian',xiayinxian_engine,if_exists='replace')
                return row

    def store_data_not(self):
        df = self.xiayingxian()
        df.to_csv('xiayinxian.csv')

    # 把股票代码放入redis
    def redis_init(self):
        rds = redis.StrictRedis(REDIS_HOST, 6379, db=0)
        rds_2 = redis.StrictRedis(REDIS_HOST, 6379, db=1)
        for i in rds.keys():
            d = dict({i: rds.get(i)})
            rds_2.lpush('codes', d)

    # 正确的模板
    def get_hist_line(self, date):
        print "Starting to capture"
        cmd = 'select * from `{}` where datetime = \'{}\''
        r0 = redis.StrictRedis(REDIS_HOST, 6379, db=0)
        for code in r0.keys():
            try:
                cursor.execute(cmd.format(code, date))
            except Exception, e:
                continue
            data = cursor.fetchall()
            #
            try:
                data_row = data[0]
            except Exception, e:
                continue
            d = dict(zip(('datetime','code', 'name', 'open', 'close', 'high', 'low'), data_row[1:8]))
            self._xiayingxian(d, 0.7)


# 把股票代码放到redis
def add_code_redis():
    rds = redis.StrictRedis(REDIS_HOST, 6379, db=0)
    rds_1 = redis.StrictRedis(REDIS_HOST, 6379, db=1)
    df = ts.get_stock_basics()
    df = df.reset_index()

    # 清理数据库
    if rds.dbsize() != 0:
        rds.flushdb()
    if rds_1.dbsize() != 0:
        rds_1.flushdb()

    for i in range(len(df)):
        code, name, timeToMarket = df.loc[i]['code'], df.loc[i]['name'], df.loc[i]['timeToMarket']
        # print str(timeToMarket)
        d = dict({code: ':'.join([name, str(timeToMarket)])})
        # print d
        rds.set(code, name)
        rds_1.lpush('codes', d)


def update_daily():
    '''
    每天更新行情
    :return:
    '''
    # 运行静态方法
    SaveData.daily_market()
    time.sleep(20)
    daily_conn = get_mysql_conn('daily')
    cursor = daily_conn.cursor()
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    cmd = 'select * from `{}`;'.format(today)
    cursor.execute(cmd)
    #today = '2017-11-17'
    #daily_df = pd.read_sql_table(today,daily_conn,index_col='index')
    days_info = cursor.fetchall()
    for i in days_info:
        code = i[1]
        name = i[2]
        close = i[4]
        opens = i[5]
        high = i[6]
        low = i[7]
        vol = i[9]
        amount = i[11]

        try:
            history_conn = get_mysql_conn('history')
            history_cur = history_conn.cursor()
            history_cur.execute('select count(*) from `{}`;'.format(code))
        except Exception,e:
            print e
            continue
        l=history_cur.fetchone()
        df = pd.DataFrame(columns=['datetime', 'code', 'name', 'open', 'close', 'high', 'low', 'vol', 'amount'])
        df.loc[l] = [today, code, name, opens, close, high, low, vol, amount]
        try:
            df.to_sql(code, engine, if_exists='append')
            print code
        except Exception, e:
            print df
            print e

def get_hist_data(code, name, start_data):
    try:
        # start_data = datetime.datetime.strptime(str(start_data), '%Y%m%d').strftime('%Y-%m-%d')

        df = ts.bar(code, conn=conn, start_date=start_data, adj='qfq')
    except Exception, e:
        print e
        return
    hist_con = get_engine('history')
    df.insert(1, 'name', name)
    df = df.reset_index()
    #print df
    df2=pd.read_sql_table(code,hist_con,index_col='index')
    try:
        new_df = pd.concat([df,df2])
        new_df = new_df.reset_index(drop=True)
        new_df.to_sql(code, engine, if_exists='replace')
    except Exception, e:
        print e
        return


class StockThread(Thread):
    def __init__(self, loop):
        Thread.__init__(self)
        self.rds = redis.StrictRedis(REDIS_HOST, 6379, db=1)
        self.loop_count = loop

    def run(self):
        self.loops()

    def loops(self):
        #start_date = datetime.datetime.now().strftime('%Y-%m-%d')
        start_date = '2017-11-21'

        while 1:
            try:
                item = self.rds.lpop('codes')
                print item
            except Exception, e:
                print e
                break

            d = eval(item)
            k = d.keys()[0]
            v = d[k]
            name = v.split(':')[0].strip()
            # start_date=v.split(':')[1].strip()

            get_hist_data(k, name, start_date)


THREAD_NUM = 4

def StoreData():
    threads = []
    for i in range(THREAD_NUM):
        t = StockThread(i)
        t.start()
        threads.append(t)

    for j in range(THREAD_NUM):
        threads[j].join()
    print 'done'


# 能够正常运行的函数
def main():
    obj = Kline()

    #obj.get_hist_line('2017-11-17')


    # obj.get_hist_line('2017-11-16')
    # obj.get_hist_line('2017-11-15')
    # obj.get_hist_line('2017-11-14')
    # obj.get_hist_line('2017-11-13')

    # 存储基本面的数据
    # obj.store_base_data('sql')

    # 获取股票的前复权数据, 使用bar函数
    # obj.store_hist_data()
    # 存放股票的代码和名字
    #add_code_redis()
    # obj.redis_init()
    # 保存历史数据
    #StoreData()

    # 把每天的数据更新到数据库
    update_daily()
    print "Done"

if __name__ == '__main__':
    main()
