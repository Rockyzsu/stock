# -*-coding=utf-8-*-
# 估价达到自己的设定值,发邮件通知, 每天2.45发邮件
import tushare as ts
from setting import sendmail,get_engine,trading_time
import datetime
import time
import pandas as pd
import tushare as ts

class ReachTarget():
    def __init__(self):
        self.cb_code = self.bond()
        self.api = ts.get_apis()

    def bond(self):
        engine = get_engine('db_bond')
        bond_table = 'tb_bond_jisilu'
        jsl_df = pd.read_sql(bond_table, engine,index_col='index')
        return jsl_df[u'正股代码'].values

    def monitor(self):
        while 1:

            # if trading_time():
            if True:
                price_list = ts.quotes(self.cb_code,conn=self.api)
                print price_list
                time.sleep(60)
            else:
                time.sleep(60)




if __name__ == '__main__':
    obj = ReachTarget()
    obj.monitor()
