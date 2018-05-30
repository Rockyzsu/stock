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
from filter_stock import Filter_Stock
def get_data():
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

# 找一些新股的可转债
def get_zhenggu():
    df = pd.read_sql('tb_bond_jisilu',get_engine('db_bond'))
    code_list = df[u'正股代码'].values
    obj = Filter_Stock()
    ns_df = obj.get_new_stock('2015','2018')
    zg_code = ns_df[ns_df['code'].isin(code_list)]['code'].values

    ret_df = df[df[u'正股代码'].isin(zg_code)][[u'可转债代码',u'可转债名称',u'正股名称',u'溢价率',u'可转债价格']]
    print ret_df
    with open('new_stock_zzk.txt','w') as f:
        s = '\n'.join(list(ret_df[u'可转债代码'].values))
        f.write(s)

if __name__=="__main__":
    get_zhenggu()