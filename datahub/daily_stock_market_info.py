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
import os
from sqlalchemy import VARCHAR

import sys
sys.path.append('..')
from common.BaseService import BaseService
from configure.settings import DBSelector,config_dict

FIX_TABLE_NAME = 'astock_market'

class FetchDaily(BaseService):
    def __init__(self):
        super(FetchDaily, self).__init__(f'../log/{self.__class__.__name__}.log')

        self.path = config_dict('data_path')
        self.check_path(self.path)
        self.df_today_all = pd.DataFrame()
        self.TIMEOUT = 10
        self.DB = DBSelector()
        self.engine = self.DB.get_engine('db_daily', 'qq')

    def transfer_db(self,df):
        self.engine_tf = self.DB.get_engine('ptrade', 'qq')
        try:
            df.to_sql(FIX_TABLE_NAME, self.engine_tf, if_exists='replace', index=True, dtype={'code': VARCHAR(6)})
        except Exception as e:
            self.logger.info(e)
            self.notify(f'{__file__}报错')

    def get_today_market(self, re_try=10):

        while re_try > 0:
            try:
                df = ts.get_today_all()
                if df is None:
                    continue
                if len(df) == 0:
                    continue
            except Exception as  e:
                self.logger.error(e)
                re_try = re_try - 1
                time.sleep(self.TIMEOUT)
            else:
                return df

        return None

    def run(self):

        self.df_today_all = self.get_today_market()
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
                self.notify(title=f'{self.__class__}写excel出错')
                self.logger.error(e)


            try:
                self.df_today_all['code'] = self.df_today_all['code'].astype(str)
                self.df_today_all.drop_duplicates(subset='code', keep='first', inplace=True)
                self.df_today_all.to_sql(self.today, self.engine, if_exists='replace',dtype={'code': VARCHAR(6)})
                self.transfer_db(self.df_today_all)

            except Exception as e:
                self.notify(title=f'{__file__} mysql出错')
                self.logger.error(e)



def main():
    obj = FetchDaily()
    obj.run()

if __name__ == "__main__":
    main()

