# -*-coding=utf-8-*-
# 保存数据到本地mysq数据库
import datetime
import redis
import os
import tushare as ts
from sqlalchemy import create_engine
import pandas as pd
from setting import engine
import MySQLdb
HOSTNAME='localhost'
class StoreDB():
    def __init__(self):
        self.cons = ts.get_apis()
        self.engine = create_engine('mysql+pymysql://root:password@localhost:3306/stock?charset=utf8')
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
        self.engine = create_engine('mysql+pymysql://root:123456z@localhost:3306/stock?charset=utf8')


    def store_data(self,month):
        filename = os.path.join(self.data_folder,'2017-0{0}.csv'.format(month))
        print filename
        df =pd.read_csv(filename,encoding='gbk')

        print df
        df.to_sql('delivery',self.engine,if_exists='append')

# 保存市场的基本信息
def save_baseinfo():
    df = ts.get_stock_basics()
    #print df
    df = df.reset_index()
    df.to_sql('baseinfo',engine)

#删除已存在的股票代码数据库
def del_db():
    r=redis.StrictRedis(HOSTNAME,6379,db=0)
    db = MySQLdb.connect('localhost','root','123456z','stock')
    cursor =db.cursor()
    for i in r.keys():
        #print i
        cmd='drop table if exists `{}`'.format(i)
        print cmd
        try:
            cursor.execute(cmd)
        except Exception,e:
            print e


    #print len(r.keys())

if __name__ == '__main__':
    #obj = StoreDB()
    #obj.start()
    '''
    obj = DeliveryOrder()
    for i in range(1,9):
        obj.store_data(str(i))
    '''
    #save_baseinfo()
    del_db()