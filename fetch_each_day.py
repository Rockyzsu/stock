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
from settings import DBSelector, llogger, is_holiday, DATA_PATH

logger = llogger('log/fetch_each_day.log')


class FetchDaily(object):
    def __init__(self):

        self.today = datetime.datetime.now().strftime('%Y-%m-%d')
        # self.TODAY = '2020-02-07'
        self.path = DATA_PATH
        if not os.path.exists(self.path):
            try:
                os.mkdir(self.path)
            except Exception as e:
                print(e)

        self.df_today_all = pd.DataFrame()
        self.TIMEOUT = 10
        self.DB = DBSelector()

    def gettodaymarket(self, re_try=10):
        while re_try > 0:
            try:
                df = ts.get_today_all()
                if df is None:
                    continue
                if len(df) == 0:
                    continue
            except Exception as  e:
                logger.error(e)

                re_try = re_try - 1
                time.sleep(self.TIMEOUT)
                # import tushare as ts
            else:
                return df

        return None

    def store(self):
        self.df_today_all = self.gettodaymarket()
        # 存储每天 涨幅排行  榜,避免每次读取耗时过长
        filename = self.today + '_all_.xls'
        # 放在data文件夹下
        full_filename = os.path.join(self.path, filename)
        if self.df_today_all is not None:
            # 保留小数点的后两位数
            self.df_today_all['turnoverratio'] = self.df_today_all['turnoverratio'].map(lambda x: round(x, 2))
            self.df_today_all['per'] = self.df_today_all['per'].map(lambda x: round(x, 2))
            self.df_today_all['pb'] = self.df_today_all['pb'].map(lambda x: round(x, 2))
            try:
                self.df_today_all.to_excel(full_filename)
            except Exception as  e:
                logger.error(e)

            engine = self.DB.get_engine('db_daily','qq')
            # print(self.df_today_all)
            try:
                self.df_today_all.to_sql(self.today, engine, if_exists='fail')
            except Exception as e:
                # print(e)
                logger.error(e)
        else:
            logger.error('today_all df is None')

    def store_new(self):
        self.df_today_all = self.gettodaymarket()
        filename = self.today + '_all_.xls'
        full_filename = os.path.join(self.path, filename)
        if not os.path.exists(full_filename):
            if self.df_today_all is not None:
                try:
                    self.save_to_excel(self.df_today_all, full_filename)
                except Exception as e:
                    print(e)
                engine = self.DB.get_engine('db_daily','qq')
                try:
                    self.df_today_all.to_sql(self.today, engine)
                except Exception as e:
                    print(e)
                    pass

    def save_to_excel(self, df, filename, encoding='gbk'):
        try:
            df.to_csv('temp.csv', encoding=encoding, index=False)
            df = pd.read_csv('temp.csv', encoding=encoding, dtype={'code': str})
            df.to_excel(filename, encoding=encoding)
            return True
        except Exception as e:
            print("Save to excel faile")
            print(e)
            return None


if __name__ == "__main__":

    if is_holiday():
        logger.info("Holidy")
        exit()
    logger.info("Start")
    obj = FetchDaily()
    obj.store()
