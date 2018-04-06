# -*-coding=utf-8-*-
import datetime
import sys

__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''

import pandas as pd
import talib
import tushare as ts
import matplotlib as mpl
from mpl_finance import candlestick2_ochl,volume_overlay
from matplotlib  import pyplot as plt
mpl.rcParams['font.sans-serif'] = ['simhei']
mpl.rcParams['axes.unicode_minus'] = False
api=ts.get_apis()
def plot_stock_line(code,name,start='2017-10-01'):
    today =datetime.datetime.now().strftime('%Y-%m-%d')
    fig = plt.figure(figsize=(10,8))
    # fig,(ax,ax2)=plt.subplots(2,1,sharex=True,figsize=(16,10))
    ax=fig.add_axes([0,0.3,1,0.55])
    ax2=fig.add_axes([0,0.1,1,0.25])
    df = ts.bar(code,conn=api,start_date=start)
    # df=df.sort_values(by='datetime')
    df = df.sort_index()
    # print df.head(5)
    # name=u'和顺电气'
    # name=''
    df =df.reset_index()
    # df = ts.get_k_data('300141',start='2018-03-01')
    # df['date']=df['date'].dt.strftime('%Y-%m-%d')
    df['datetime']=df['datetime'].dt.strftime('%Y-%m-%d')
    sma5=talib.SMA(df['close'].values,5)
    sma20=talib.SMA(df['close'].values,10)
    # ax.set_xticks(range(0,len(df),20))
    # # ax.set_xticklabels(df['date'][::5])
    # ax.set_xticklabels(df['datetime'][::20])
    candlestick2_ochl(ax,df['open'],df['close'],df['high'],df['low'],width=0.5,colorup='r',colordown='g',alpha=0.6)
    ax.set_title(u'{} {} {}'.format(today,code,name))
    # ax.set_title(u'测试')
    ax.plot(sma5)
    ax.plot(sma20)


    # df['vol'].plot(kind='bar')
    volume_overlay(ax2,df['open'],df['close'],df['vol'],width=0.5,alpha=0.8,colordown='g',colorup='r')
    ax2.set_xticks(range(0,len(df),10))
    # ax.set_xticklabels(df['date'][::5])
    ax2.set_xticklabels(df['datetime'][::10])
    # ax2.grid(True)

    plt.setp(ax2.get_xticklabels(), rotation=30, horizontalalignment='right')
    # plt.grid(True)
    # plt.subplots_adjust(hspace=0)
    plt.show()

if __name__ == '__main__':
    if len((sys.argv))>2:
        code = sys.argv[1]
    else:
        code='603598'
    plot_stock_line(code,'2017-10-01')
    ts.close_apis(api)