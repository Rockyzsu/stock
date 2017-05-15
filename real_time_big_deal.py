# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''

import tushare as ts
import pandas as pd
import time,os
import numpy as np
pd.set_option('display.max_rows',None)
class BigMonitor():
    def __init__(self):
        path=os.path.join(os.getcwd(),'data')
        if os.path.exists(path)==False:
            os.mkdir(path)
            print "Please put data under data folder"
            exit()
        os.chdir(path)

        self.bases=pd.read_csv('bases.csv',dtype={'code':np.str})

    def loop(self,code):
        name=self.bases[self.bases['code']==code]['name'].values[0]
        print name
        while 1:
            time.sleep(2)
            df_t1=ts.get_realtime_quotes(code)
            v1=long(df_t1['volume'].values[0])
            #print df_t1
            time.sleep(2)
            df_t2=ts.get_realtime_quotes(code)
            v2=long(df_t2['volume'].values[0])
            delta= v2-v1
            if delta >10000:
                print "Big deal"
                print delta

def main():
    obj=BigMonitor()
    obj.loop('002868')

main()