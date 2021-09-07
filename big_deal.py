#-*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
import tushare as ts
#搜索大单进入的个股
import pandas as pd
from toolkit import Toolkit
import os
import numpy as np
pd.set_option('display.max_rows',None)
class Monitor_Stock():
    def __init__(self):
        self.mystock=Toolkit.read_stock('mystock.csv')
        self.base=pd.read_csv('bases.csv',dtype={'code': np.str})
        #print(self.base)
    #大于某手的大单
    def getBigDeal(self, code,vol):
        df = ts.get_today_ticks(code)
        t= df[df['volume']>vol]
        s=df[df['amount']>100000000]
        print('\n')
        if t.size!=0:
            print("Big volume")
            print(self.base[self.base['code']==str(code)]['name'].values[0])
            print(t)
        if s.size!=0:
            print("Big amount: ")
            print(self.base[self.base['code']==str(code)]['name'].values[0])
            print(s)
        r=df[df['volume']>vol*10]
        if r.size!=0:
            print("Super amount:")
            print(self.base[self.base['code']==str(code)]['name'].values[0])
            print(r)


    def loops(self):
        for i in self.mystock:
            self.getBigDeal(i,1000)



def main():
    if ts.__version__ != '0.7.5':
        print("Make sure using tushare 0.7.5")
        exit()
    current = os.getcwd()
    folder = os.path.join(current, 'data')
    if os.path.exists(folder) == False:
        os.mkdir(folder)
    os.chdir(folder)
    obj=Monitor_Stock()
    #obj.getBigDeal('002451',2000)
    obj.loops()


main()
