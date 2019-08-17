#-*-coding=utf-8-*-

import tushare as ts
from pandas import Series
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pylab import mpl
#mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei']    # 指定默认字体：解决plot不能显示中文问题
mpl.rcParams['axes.unicode_minus'] = False
# 每个月的解禁股与大盘指数的关系
def ban_share(code,name):
    conn =ts.get_apis()
    year_2017 = [2629.218,3970.902,2083.032,1720.327,1999.456,1771.074,2417.082,2904.992,2910.946,2971.483,2350.122,3874.328]
    df = ts.bar(code, conn=conn, freq='M', start_date='2016-12-30', end_date='2017-11-01', asset='INDEX')
    series = df['close']
    '''
    diff_series=[]
    print(series)
    l = len(series)
    for i in range(l-1):
        print(series[i])
        d= series[i]-series[i+1]
        diff_series.append(d)
    #print(len(diff_series))
    '''

    #s2=Series(series)
    s2=series[:len(series)-1]
    s3 = s2.sort_index(ascending=True)
    #print(s3)
    s1 = Series(year_2017[0:len(s3)])
    s3=s3.reset_index(drop=True)
    #print(s3)
    #print(s1)
    cor = s3.corr(s1)
    #print(len(s3))
    #print(len(s1))
    print(cor)
    plt.figure()
    plt.subplot(2,1,1)
    s1.plot()
    plt.subplot(2,1,2)
    s3.plot(title=name)
    plt.show()

    if abs(cor) >0.5:
        print('Great factor: ',code)

def read_index():
    df = pd.read_excel('data/index_data.xls')
    df['index_data']=df['index_data'].apply(lambda x:str(x).zfill(6))
    #print(df)
    #df['index_data'].apply(lambda x:ban_share(x))
    for i in range(len(df)):
        code = df.loc[i]['index_data']
        name =df.loc[i]['name']
        ban_share(code,name)
def main():
    read_index()
    #ban_share('000001')
    print('Done')
main()