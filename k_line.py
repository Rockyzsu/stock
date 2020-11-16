# -*-coding=utf-8-*-
# 获取 不同形态的k线
import random
import time
import tushare as ts
import pandas as pd
import os, datetime, math
import numpy as np
import logging
from configure.settings import DBSelector, MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, REDIS_HOST
import redis
from threading import Thread
from common.BaseService import  BaseService

DB = DBSelector()
engine = DB.get_engine('history', 'qq')
conn = ts.get_apis()
MYSQL_DB = 'history'
cursor = DB.get_mysql_conn(MYSQL_DB, 'qq').cursor()


# pd.set_option('display.max_rows', None)

class Kline(BaseService):
    def __init__(self):
        super(Kline, self).__init__('log/kline.log')

        path = os.path.join(os.getcwd(), 'data')
        self.today_date = datetime.datetime.now().strftime('%Y-%m-%d')

        if not os.path.exists(path):
            os.mkdir(path)
        os.chdir(path)

    def store_base_data(self, target):
        self.all_info = ts.get_stock_basics()
        self.all_info = self.all_info.reset_index()
        print(self.all_info)
        if target == 'sql':
            self.all_info.to_sql('tb_baseinfo', engine, if_exists='replace')

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
            print(code, name, start_date)

    # 获取历史行情，前复权 ，使用bar函数，get_hist_data 经常会出错
    def get_hist_data(self, code, name, start_data):
        try:
            start_data = datetime.datetime.strptime(str(start_data), '%Y%m%d').strftime('%Y-%m-%d')
            df = ts.bar(code, conn=conn, start_date=start_data, adj='qfq')
            print(df)
        except Exception as e:
            print(e)
            return

        df.insert(1, 'name', name)
        df = df.reset_index()
        try:
            df.to_sql(code, engine, if_exists='append')
        except Exception as e:
            print(e)

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
        # print(open_p)
        closed = float(row['close'])
        # print(closed)
        low = float(row['low'])
        # print(low)
        high = float(row['high'])
        p = min(closed, open_p)
        try:
            diff = (p - low) * 1.00 / (high - low)
            diff = round(diff, 3)
        except ZeroDivisionError:
            diff = 0
        if diff > ratio:
            xiayinxian_engine = DB.get_engine('db_selection','qq')
            date, code, name, ocupy_ration, standards = row['datetime'], row['code'], row['name'], diff, ratio
            df = pd.DataFrame(
                {'datetime': [date], 'code': [code], 'name': [name], 'ocupy_ration': [ocupy_ration],
                 'standards': [standards]})
            try:
                df1 = pd.read_sql_table('xiayingxian', xiayinxian_engine, index_col='index')
                df = pd.concat([df1, df])
            except Exception as e:
                print(e)
                # return None

            df = df.reset_index(drop=True)
            df.to_sql('xiayingxian', xiayinxian_engine, if_exists='replace')
            return row

    def store_data_not(self):
        df = self._xiayingxian()
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
        print("Starting to capture")
        cmd = 'select * from `{}` where datetime = \'{}\''
        r0 = redis.StrictRedis(REDIS_HOST, 6379, db=0)
        for code in r0.keys():
            try:
                cursor.execute(cmd.format(code, date))
            except Exception as e:
                continue
            data = cursor.fetchall()
            #
            try:
                data_row = data[0]
            except Exception as e:
                continue
            d = dict(zip(('datetime', 'code', 'name', 'open', 'close', 'high', 'low'), data_row[1:8]))
            self._xiayingxian(d, 0.7)


    # 把股票代码放到redis
    def add_code_redis(self):
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
            # print(str(timeToMarket))
            d = dict({code: ':'.join([name, str(timeToMarket)])})
            # print(d)
            rds.set(code, name)
            rds_1.lpush('codes', d)




def get_hist_data(code, name, start_data):
    try:
        # start_data = datetime.datetime.strptime(str(start_data), '%Y%m%d').strftime('%Y-%m-%d')

        df = ts.bar(code, conn=conn, start_date=start_data, adj='qfq')
    except Exception as e:
        print(e)
        return
    hist_con = DB.get_engine('history')
    df.insert(1, 'name', name)
    df = df.reset_index()
    df2 = pd.read_sql_table(code, hist_con, index_col='index')

    try:
        new_df = pd.concat([df, df2])
        new_df = new_df.reset_index(drop=True)
        new_df.to_sql(code, engine, if_exists='replace')
    except Exception as e:
        print(e)
        return


class StockThread(Thread):
    def __init__(self, loop):
        Thread.__init__(self)
        self.rds = redis.StrictRedis(REDIS_HOST, 6379, db=1)
        self.loop_count = loop

    def run(self):
        self.loops()

    def loops(self):
        # start_date = datetime.datetime.now().strftime('%Y-%m-%d')
        start_date = '2017-11-21'

        while 1:
            try:
                item = self.rds.lpop('codes')
                print(item)
            except Exception as e:
                print(e)
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
    print('done')


# 能够正常运行的函数
def main():
    obj = Kline()

    # obj.get_hist_line('2017-11-17')

    # obj.get_hist_line('2017-11-16')
    # obj.get_hist_line('2017-11-15')
    # obj.get_hist_line('2017-11-14')
    # obj.get_hist_line('2017-11-13')

    # 存储基本面的数据
    # obj.store_base_data('sql')

    # 获取股票的前复权数据, 使用bar函数
    # obj.store_hist_data()
    # 存放股票的代码和名字
    # add_code_redis()
    # obj.redis_init()
    # 保存历史数据
    # StoreData()



if __name__ == '__main__':
    main()
