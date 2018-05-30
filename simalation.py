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
from setting import get_engine,get_mysql_conn


class Simulation():

    def __init__(self):
        path = os.path.join(os.getcwd(), 'data')
        if os.path.exists(path) == False:
            os.mkdir(path)
        os.chdir(path)
        self.today = datetime.datetime.now().strftime('%Y-%m-%d')

    def caculation(self):
        self.name = 'simulation.xls'
        self.df = pd.read_excel(self.name)
        self.df[u'代码'] = self.df[u'代码'].map(lambda x: str(x).zfill(6))
        self.base = pd.read_csv('bases.csv', dtype={'code': np.str})
        engine = get_engine('db_daily')
        df_t = pd.read_sql(self.today, engine, index_col='index')

        print self.df[u'代码'].values
        for i in self.df[u'代码'].values:
            name = self.base[self.base['code'] == i]['name'].values[0]
            print name
            t = name.decode('utf-8')
            print
            print type(t)
            # print chardet.detect(t)
            self.df.ix[self.df[u'代码'] == i, u'当前日期'] = self.today
            # t=ts.get_k_data(i)

            pchange = df_t.ix[df_t['code'] == i, 'changepercent'].values[0]
            print pchange
            self.df.ix[self.df[u'代码'] == i, u'今日涨幅'] = pchange
            current = df_t[df_t['code'] == i]['trade'].values[0]
            self.df.ix[self.df[u'代码'] == i, u'当前价格'] = current
            current_profit = (current - self.df[self.df[u'代码'] == i][u'买入价格'].values[0]) / \
                             self.df[self.df[u'代码'] == i][u'买入价格'].values[0]
            self.df.ix[self.df[u'代码'] == i, u'目前盈亏'] = round(current_profit * 100, 2)
            print current_profit
        print self.df
        self.df.to_excel(self.name, encoding='utf-8')

    def calculation_sql(self):
        engine = get_engine('db_daily')
        df = pd.read_sql(self.today, engine, index_col='index')
        conn = get_mysql_conn('db_stock')
        cur = conn.cursor()
        cur.execute('select * from tb_simulation')
        ret = cur.fetchall()
        for item in ret:
            code = item[3]
            b_price = item[5]
            # 旧版字段
            current = df[df['code']==code]['trade'].values[0]
            # current = df[df['code']==code]['price'].values[0]

            profit = round((current-b_price)/b_price*100,2)
            p_change = df[df['code']==code]['changepercent'].values[0]
            # p_change = df[df['code']==code]['p_change'].values[0]
            cmd = u'update tb_simulation set `当前日期`=\'{}\', `当前价格`={}, `今日涨幅`={},`盈亏比例`={}  where `代码`=\'{}\''.format(self.today,current,round(p_change,2),profit,code)
            cur.execute(cmd)
            try:
                conn.commit()
            except:
                conn.rollback()

def main():
    obj = Simulation()
    obj.calculation_sql()

if __name__ == '__main__':
    main()
