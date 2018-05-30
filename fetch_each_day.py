# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
# 获取每天的行情信息
import tushare as ts
import pandas as pd
import time
import datetime
import os
from setting import get_engine


class FetchDaily:
    def __init__(self):
        # self.today = '2018-08-16'
        self.today = datetime.datetime.now().strftime('%Y-%m-%d')
        if ts.is_holiday(self.today):
            exit()
        self.path = os.path.join(os.path.dirname(__file__), 'data')
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        self.df_today_all = pd.DataFrame()
        self.TIMEOUT = 10

    def gettodaymarket(self, re_try=5):
        while re_try > 0:
            try:
                df = ts.get_today_all()
                if len(df) != 0:
                    return df
            except Exception, e:
                print e
                re_try = re_try - 1
                time.sleep(self.TIMEOUT)
        return None

    def store(self):
        self.df_today_all = self.gettodaymarket()
        # 存储每天 涨幅排行  榜,避免每次读取耗时过长
        filename = self.today + '_all_.xls'
        # 放在data文件夹下
        full_filename = os.path.join(self.path, filename)
        if not os.path.exists(full_filename):
            if self.df_today_all is not None:
                # 保留小数点的后两位数
                self.df_today_all['turnoverratio'] = map(lambda x: round(x, 2), self.df_today_all['turnoverratio'])
                self.df_today_all['per'] = map(lambda x: round(x, 2), self.df_today_all['per'])
                self.df_today_all['pb'] = map(lambda x: round(x, 2), self.df_today_all['pb'])
                try:
                    self.df_today_all.to_excel(full_filename)
                except Exception, e:
                    print e
                engine = get_engine('db_daily')
                # print self.df_today_all
                try:
                    self.df_today_all.to_sql(self.today, engine,if_exists='fail')
                except Exception, e:
                    print e
                    pass

    def store_new(self):
        self.df_today_all = self.gettodaymarket()
        filename = self.today + '_all_.xls'
        full_filename = os.path.join(self.path, filename)
        if not os.path.exists(full_filename):
            if self.df_today_all is not None:
                try:
                    self.save_to_excel(self.df_today_all,full_filename)
                except Exception, e:
                    print e
                engine = get_engine('db_daily')
                try:
                    self.df_today_all.to_sql(self.today, engine)
                except Exception, e:
                    print e
                    pass

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
if __name__ == "__main__":
    obj = FetchDaily()
    # obj.store_new()
    obj.store()