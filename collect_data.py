#-*-coding=utf-8-*-
# 每天收盘收运行
import datetime

__author__ = 'Rocky'
import tushare as ts
import os
from setting import get_engine,get_mysql_conn
import pandas as pd
import pandas
daily_engine=get_engine('daily')
class SaveData():
    def __init__(self):
        current=os.getcwd()
        work_space=os.path.join(current,'data')
        if os.path.exists(work_space) ==False:
            os.mkdir(work_space)
        os.chdir(work_space)
        self.today= datetime.datetime.now().strftime("%Y-%m-%d")

    #当天创新低的股票
    def daily_market(self):
        df = ts.get_today_all()
        try:
            df.to_sql(self.today,daily_engine,if_exists='replace')
        except Exception,e:
            print e
        print "Save {} data to MySQL".format(self.today)