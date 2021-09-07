# -*- coding: UTF-8 -*-
"""
@author:xda
@file:util.py
@time:2021/01/24
"""
import json
import pandas as pd
import re


def jsonp2json(str_):
    return json.loads(str_[str_.find('{'):str_.rfind('}') + 1])


def bond_filter(code):
    m = re.search('^(11|12)', code)
    return True if m else False


def get_holding_list(filename=None):
    '''
    获取持仓列表
    '''
    print(filename)
    df = pd.read_csv(filename, encoding='gbk')
    # print(df.head())
    df['证券代码'] = df['证券代码'].astype(str)
    df['kzz'] = df['证券代码'].map(bond_filter)
    df = df[df['kzz'] == True]
    return df['证券代码'].tolist()


if __name__ == '__main__':
    print(get_holding_list(r'D:\holding.csv'))
