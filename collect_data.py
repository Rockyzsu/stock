#-*-coding=utf-8-*-
# 每天收盘收运行
import datetime

__author__ = 'Rocky'
import tushare as ts
import os
from setting import get_engine,LLogger
import pandas as pd
logger=LLogger('collect_data.log')

class SaveData():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    daily_engine = get_engine('daily')

    def __init__(self):
        current=os.getcwd()
        work_space=os.path.join(current,'data')
        if os.path.exists(work_space) ==False:
            os.mkdir(work_space)
        os.chdir(work_space)


    @staticmethod
    def daily_market():
        df = ts.get_today_all()
        try:
            df.to_sql(SaveData.today,SaveData.daily_engine,if_exists='replace')
        except Exception,e:
            print e
        print "Save {} data to MySQL".format(SaveData.today)

    #获取解禁股
    def get_classified_stock(self,year=None,month=None):
        df=ts.xsg_data(year,month)
        filename='{}-{}-classified_stock.xls'.format(year,month)
        self.save_to_excel(df,filename)

    def basic_info(self):
        engine = get_engine('db_stock')
        df = ts.get_stock_basics()
        if df is not None:
            try:
                df=df.reset_index()
                df[u'更新日期']=datetime.datetime.now().strftime('%Y-%m-%d')
                df.to_sql('tb_basic_info',engine,if_exists='replace')
            except Exception,e:
                print e

    def save_to_excel(self,df,filename,encoding='gbk'):
        try:
            df.to_csv('temp.csv',encoding=encoding,index=False)
            df=pd.read_csv('temp.csv',encoding=encoding,dtype={'code':str})
            df.to_excel(filename,encoding=encoding)
            return True
        except Exception,e:
            print "Save to excel faile"
            print e
            return None


def main():
    obj=SaveData()
    obj.basic_info()

if __name__=='__main__':
    today =  datetime.datetime.now().strftime('%Y-%m-%d')
    if ts.is_holiday(today):
        logger.log('{} holiday'.format(today))
        exit(0)
    main()
    # SaveData.daily_market()
    # obj.get_classified_stock(2018,1)