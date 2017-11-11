# -*-coding=utf-8-*-
# 保存数据到本地mysq数据库
import datetime

import os
import tushare as ts
from sqlalchemy import create_engine
import pandas as pd


class StoreDB():
    def __init__(self):
        self.cons = ts.get_apis()
        self.engine = create_engine('mysql+pymysql://root:123456z@localhost:3306/stock?charset=utf8')

        self.all_info = ts.get_stock_basics()
        self.all_codes = self.all_info.index

    def start(self):

        # print list(self.all_codes)
        # print type(self.all_codes)
        for index in self.all_info.index:
            # print self.all_info.ix[eachItem].values[0:-1]
            # print eachItem.index()
            # print eachItem['timeToMarket']
            code = index
            timeToMarket = self.all_info.ix[code]['timeToMarket']
            if code and timeToMarket:
                timeToMarket= datetime.datetime.strptime(str(timeToMarket),'%Y%m%d').strftime('%Y-%m-%d')
                #print timeToMarket
                self.store(code, timeToMarket)


    def store(self, code, start_date):
        #print code,start_date
        try:
            print code
            print start_date
            df = ts.bar(code=code, conn=self.cons,start_date=start_date)

        except Exception,e:
            print e
            return
        try:
            df.to_sql(code, self.engine)
        except Exception,e:
            print e
            return
        #print df

class DeliveryOrder():
    def __init__(self):
        self.data_folder = os.path.join(os.getcwd(),'data')
        self.engine = create_engine('mysql+pymysql://root:123456z@localhost:3306/db_parker?charset=utf8')


    def store_data(self,month):
        filename = os.path.join(self.data_folder,'2017-0{0}.csv'.format(month))
        print filename
        df =pd.read_csv(filename,encoding='gbk')

        print df
        df.to_sql('delivery',self.engine,if_exists='append')


if __name__ == '__main__':
    #obj = StoreDB()
    #obj.start()
    obj = DeliveryOrder()
    for i in range(1,10):
        obj.store_data(str(i))