# -*-coding=utf-8-*-
import datetime
import os
import random
import time
from optparse import OptionParser

__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''

import pandas as pd
import talib
import tushare as ts
import matplotlib as mpl
from mpl_finance import candlestick2_ochl, volume_overlay
import matplotlib.pyplot as plt
from configure.settings import DBSelector
import sys

if sys.platform=='linux':
    # centos的配置, 根据自定义拷贝的字体
    mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei']
else:
    mpl.rcParams['font.sans-serif'] = ['simhei']


mpl.rcParams['axes.unicode_minus'] = False



def get_basic_info():
    DB = DBSelector()
    engine = DB.get_engine('db_stock', 'qq')
    base_info = pd.read_sql('tb_basic_info', engine, index_col='index')
    return base_info

def check_path(root_path,current,filename):
    folder_path = os.path.join(root_path, current)
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    full_path = os.path.join(folder_path, filename)

    if os.path.exists(full_path):
        return None
    else:
        return full_path

def plot_stock_line(api,code, name, table_type, current, root_path,start='2019-10-01', save=False):

    title = '{}_{}_{}_{}'.format(current, code, name, table_type).replace('*', '_')
    filename = title + '.png'
    full_path = check_path(root_path,current,filename)
    if full_path is None:
        return

    base_info = get_basic_info()
    if code is None and name is not None:
        code = base_info[base_info['name'] == name]['code'].values[0]

    df = None
    for _ in range(4):

        try:
            df = ts.bar(code, conn=api, start_date=start)

        except Exception as e:
            ts.close_apis(api)
            time.sleep(random.random() * 30)
            api = ts.get_apis()

        else:
            break

    if df is None:
        return

    df = df.sort_index()

    if name is None:
        name = base_info[base_info['code'] == code]['name'].values[0]

    df = df.reset_index()
    df['datetime'] = df['datetime'].dt.strftime('%Y-%m-%d')
    sma5 = talib.SMA(df['close'].values, 5)
    sma20 = talib.SMA(df['close'].values, 10)
    # ax.set_xticks(range(0,len(df),20))
    # # ax.set_xticklabels(df['date'][::5])
    # ax.set_xticklabels(df['datetime'][::20])
    fig = plt.figure(figsize=(10, 8))
    # fig,(ax,ax2)=plt.subplots(2,1,sharex=True,figsize=(16,10))
    ax = fig.add_axes([0, 0.3, 1, 0.50])
    ax2 = fig.add_axes([0, 0.1, 1, 0.20])

    candlestick2_ochl(ax, df['open'], df['close'], df['high'], df['low'], width=1, colorup='r', colordown='g',
                      alpha=0.6)
    ax.grid(True)
    ax.set_title(title)
    ax.plot(sma5, label='MA5')
    ax.legend()
    ax.plot(sma20, label='MA20')
    ax.legend(loc=2)
    ax.grid(True)
    # df['vol'].plot(kind='bar')
    volume_overlay(ax2, df['open'], df['close'], df['vol'], width=0.75, alpha=0.8, colordown='g', colorup='r')
    ax2.set_xticks(range(0, len(df), 20))
    # ax.set_xticklabels(df['date'][::5])
    ax2.set_xticklabels(df['datetime'][::20])
    plt.setp(ax2.get_xticklabels(), rotation=30, horizontalalignment='right')
    ax2.grid(True)
    plt.subplots_adjust(hspace=0.3)

    if save:
        # path = os.path.join(os.path.dirname(__file__),'data',TODAY)
        fig.savefig(full_path)
    else:
        plt.show()

    plt.close()



if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-c", "--code",
                      dest="code",
                      help="-c 300141 #using code to find security")
    parser.add_option("-n", "--name",
                      dest="name",
                      help="-n  和顺电气 #using code to find security")

    (options, args) = parser.parse_args()

    if len((sys.argv)) >= 2:
        code = options.code
        name = options.name
        name = name.decode('utf-8')
    else:
        code = None
        name = '泰永长征'
    plot_stock_line(code=code, name=name, table_name='zdt', current='20180912', start='2018-02-01', save=False)
