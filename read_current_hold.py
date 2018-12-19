# -*-coding=utf-8-*-

# @Time : 2018/12/3 15:46
# @File : read_current_hold.py

import pandas as pd
import numpy as np
import tushare as ts

# 读取当前的持仓数据
# 国金证券

# 设置大于2个点就报警
ALERT_PERCENTAGE = 2

def gjzq(file):
    df = pd.read_table(file, encoding='gbk', dtype={'证券代码': np.str})
    del df['Unnamed: 15']
    code_list = list(df['证券代码'].values)

    api = ts.get_apis()

    # 移除非法证券代码 中签
    t=[code_list.remove(i) for i in code_list.copy() if i.startswith('7') or i[:2] == '07']


    price_df = ts.quotes(code_list, conn=api)
    # 去除不合法的数据
    price_df=price_df.dropna()
    filter_df = price_df[price_df['last_close'] != 0]
    filter_df = filter_df.reset_index(drop=True)
    filter_df['percent'] = (filter_df['price'] - filter_df['last_close']) / filter_df['last_close'] * 100
    filter_df['percent'] = filter_df['percent'].map(lambda x: round(x, 2))
    ret_df = filter_df[(filter_df['percent'] > ALERT_PERCENTAGE) | (filter_df['percent'] < ALERT_PERCENTAGE*-1)]
    d = dict(zip(list(df['证券代码'].values), list(df['证券名称'])))
    ret_df['name']=ret_df['code'].map(lambda x:d.get(x))
    ret_df['amount']=ret_df['amount'].map(lambda x:round(x/10000,1))
    rename_column = {'code':'证券代码','name':'证券名称','price':'当前价格','percent':'涨幅','amount':'成交金额(万)'}

    ret_df=ret_df.rename(columns=rename_column)
    ret = ret_df[list(rename_column.values())]
    ret=ret.reset_index(drop=True)

    # 发送推送
    print(ret)

    ts.close_apis(api)

if __name__=='__main__':
    file='D:\OneDrive\Stock\gj_hold.xls'
    gjzq(file)