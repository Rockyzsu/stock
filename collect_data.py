#-*-coding=utf-8-*-
# 每天收盘收运行
import datetime

__author__ = 'Rocky'
import tushare as ts
import os
from setting import get_engine
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


if __name__=='__main__':
    SaveData.daily_market()