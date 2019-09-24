# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
# 模拟买入 纯粹纪录。
import os, sys, chardet
import pandas as pd
import datetime
import numpy as np
import tushare as ts
from send_mail import sender_139
from settings import get_engine, get_mysql_conn, is_holiday, llogger, DATA_PATH

filename=os.path.basename(__file__)
logger = llogger('log/'+filename)

class Simulation():

    def __init__(self):
        # path=os.path.join(os.getcwd(),'data')

        path = DATA_PATH
        if os.path.exists(path) == False:
            os.mkdir(path)
        os.chdir(path)

        self.name = 'simulation.xls'
        self.df = pd.read_excel(self.name)
        self.df['代码'] = self.df['代码'].map(lambda x: str(x).zfill(6))
        self.engine = get_engine('db_stock')
        self.engine1=get_engine('db_daily')
        # self.base = pd.read_sql('tb_basic_info', self.engine, index_col='index')
        self.money = 10000
        self.today = datetime.datetime.now().strftime('%Y-%m-%d')

    def caculation(self):
        df_t = pd.read_sql(self.today,con=self.engine1)
        # df_t = ts.get_today_all()
        for i in self.df['代码'].values:
            self.df.loc[self.df['代码'] == i, '当前日期'] = self.today

            pchange = df_t.loc[df_t['code'] == i, 'changepercent'].values[0]
            self.df.loc[self.df['代码'] == i, '今日涨幅'] = pchange

            trade = df_t[df_t['code'] == i]['trade'].values[0]
            self.df.loc[self.df['代码'] == i, '当前价格'] = trade

            current_profit = (trade - self.df[self.df['代码'] == i]['买入价格'].values[0]) / \
                             self.df[self.df['代码'] == i]['买入价格'].values[0]

            self.df.loc[self.df['代码'] == i, '目前盈亏'] = round(current_profit * 100, 2)

        self.df.to_excel(self.name, encoding='utf-8',index=None)
        self.df.to_sql('tb_simulation',self.engine,if_exists='replace')
        # ali_engine = get_engine('',False)
        # self.df.to_sql('tb_simulation',ali_engine,if_exists='replace')
        del self.df['买入理由']
        df_str = self.df.to_html()
        # print(df_str)
        sender_139('模拟盘 {}'.format(self.today),df_str,types='html')


def main():
    obj = Simulation()
    obj.caculation()

if __name__ == '__main__':
    if is_holiday():
        logger.info("Holidy")
        exit()
    logger.info("Start")

    main()
