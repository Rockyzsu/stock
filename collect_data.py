#-*-coding=utf-8-*-
# 每天收盘收运行
import datetime

__author__ = 'Rocky'
import tushare as ts
import os
from setting import get_engine
import pandas as pd
daily_engine=get_engine('daily')

class SaveData():
    today = datetime.datetime.now().strftime("%Y-%m-%d")

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
            df.to_sql(SaveData.today,daily_engine,if_exists='replace')
        except Exception,e:
            print e
        print "Save {} data to MySQL".format(SaveData.today)

    #获取解禁股
    def get_classified_stock(self,year=None,month=None):
        df=ts.xsg_data(year,month)
        filename='{}-{}-classified_stock.xls'.format(year,month)
        self.save_to_excel(df,filename)


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



if __name__=='__main__':
    # SaveData.daily_market()
    obj=SaveData()
    obj.get_classified_stock(2018,1)