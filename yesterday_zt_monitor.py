#-*-coding=utf-8-*-
from setting import get_engine
import pandas as pd
import tushare as ts
import numpy as np
engine = get_engine('db_zdt')
table='20180322zdt'
api=ts.get_apis()
df = pd.read_sql(table,engine,index_col='index')
# print df
price_list=[]
percent_list=[]
for i in df[u'代码'].values:
    try:
        curr= ts.quotes(i,conn=api)
        last_close =curr['last_close'].values[0]
        curr_price =curr['price'].values[0]
        # if last_close>=curr_price:
        # print i,
        # print df[df[u'代码']==i][u'名称'].values[0],
        # print  percent
    except Exception,e:
        print e
        curr_price=0
    if last_close==0:
        percent= np.nan
    percent = round((curr_price - last_close) * 100.00 / last_close, 2)
    percent_list.append(percent)
    price_list.append(curr_price)

df['today_price']=price_list
df['today_percent']=percent_list
# print df
df[df['today_price']==0]
df.to_sql(table+'monitor',engine,if_exists='replace')
ts.close_apis(api)

