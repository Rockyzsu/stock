# -*-coding=utf-8-*-

__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
from scipy import  stats
import tushare as ts
from setting import get_engine
import pandas as pd
engine = get_engine('db_bond')
bond_df = pd.read_sql('tb_bond_jisilu',engine,index_col='index')
# print bond_df
api = ts.get_apis()
# print bond_df
close_price=[]
for code in bond_df[u'可转债代码'].values:
    try:
        df = ts.bar(code,conn=api)
    except Exception,e:
        print e
        continue
    # print df[0]
    # print code
    print bond_df[bond_df[u'可转债代码']==code][u'可转债名称'].values[0],'\t'
    try:
        close_price.append(df.iloc[-1]['close'])
    except Exception,e:
        print e
        break


ts.close_apis(api)