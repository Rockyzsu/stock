# -*-coding=utf-8-*-
# 获取 不同形态的k线
import random
import time
import tushare as ts
import pandas as pd
import os, datetime, math
import numpy as np
import logging
from setting import engine
#pd.set_option('display.max_rows', None)

class Kline():
    def __init__(self):
        logging.info('tushare version: {}'.format(ts.__version__))
        path = os.path.join(os.getcwd(), 'data')
        self.today_date = datetime.datetime.now().strftime('%Y-%m-%d')
        logging.info(self.today_date)
        print
        if not os.path.exists(path):
            os.mkdir(path)
        os.chdir(path)
        self.conn=ts.get_apis()

    def store_base_data(self, target):
        self.all_info = ts.get_stock_basics()
        self.all_info = self.all_info.reset_index()
        print self.all_info
        if target == 'sql':
            self.all_info.to_sql('tb_baseInfo', engine)

        elif target == 'csv':
            self.all_info.to_csv('baseInfo.csv')
        else:
            logging.info('sql or csv option. Not get right argument')

    #枚举每一个股票代码
    def store_hist_data(self):
        read_cmd = 'select * from tb_baseInfo;'
        df = pd.read_sql(read_cmd,engine)
        #print df
        for i in range(len(df)):
            code,name,start_date = df.loc[i]['code'],df.loc[i]['name'],df.loc[i]['timeToMarket']
            self.get_hist_data(code,name,start_date)
            #time.sleep(random.random())
            print code,name,start_date
    # 获取历史行情，前复权 ，使用bar函数，get_hist_data 经常会出错
    def get_hist_data(self,code,name,start_data):
        try:
            start_data = datetime.datetime.strptime(str(start_data), '%Y%m%d').strftime('%Y-%m-%d')
            df = ts.bar(code,conn=self.conn,start_date=start_data,adj='qfq')
            print df
        except Exception,e:
            print e
            return

        #df.insert(0,'code',code)
        df.insert(1,'name',name)
        df = df.reset_index()
        try:
            #cmd='drop table if exists {};'.format(code)
            df.to_sql(code,engine,if_exists='replace')
        except Exception,e:
            print e

    def inital_data(self, target):
        if target=='sql':
            self.today = pd.read_csv(self.today_date + '.csv', dtype={'code': np.str})
            self.all = pd.read_csv('bases.csv', dtype={'code': np.str})


    def _xiayingxian(self, row):
        # print type(row)
        # print row
        open_p = row['open']
        # print open_p
        closed = row['trade']
        # print closed
        low = row['low']
        # print low
        settle = row['settlement']
        if open_p >= closed:
            try:
                diff = (closed - low) * 1.00 / settle * 100
            except Exception, e:
                print e

            # print diff
            if diff > 5:
                # print row['name'].decode('utf-8')
                print row['name']
                return row
        else:
            try:
                diff = (open_p - low) * 1.00 / settle * 100
            except Exception, e:
                print e

            if diff > 5:
                # print row['name'].decode('utf-8')
                print row['name']
                return row

    # 下影线
    def xiayingxian(self):
        '''
        for i in self.today:
            print i
            #not each item
        '''
        lists = []
        for i in range(len(self.today)):
            # print self.today[i]
            t = self._xiayingxian(self.today.loc[i])
            if t is not None:
                lists.append(t)
                # print i
        '''
        for i in lists:
            print type(i)
            print i
        '''
        result = pd.DataFrame(lists)
        print result
        return result

    def store_data_not(self):
        df = self.xiayingxian()
        df.to_csv('xiayinxian.csv')

# 能够正常运行的函数
def main():
    obj = Kline()
    # 存储基本面的数据
    # obj.store_base_data('sql')
    #获取股票的前复权数据, 使用bar函数
    obj.store_hist_data()

if __name__ == '__main__':
    main()