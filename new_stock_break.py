# -*-coding=utf-8-*-
__author__ = 'Rocky'
#分析新股的开板时机
import tushare as ts
import os
import pandas as pd
import numpy as np
class New_Stock_Break():
    def __init__(self):
        current = os.getcwd()
        folder = os.path.join(current, 'data')
        if os.path.exists(folder) == False:
            os.mkdir(folder)
        os.chdir(folder)
        df0=pd.read_csv('bases.csv',dtype={'code':np.str})
        self.bases=df0.sort_values('timeToMarket',ascending=False)

        #获取样本， 获取最近一个月的新股情况
        #print self.bases.dtypes

        self.cxg=self.bases[self.bases['timeToMarket']>20170401]
        self.codes= self.cxg['code'].values
        #print self.codes


    def calc_open_day(self,code):
        cont=100000000
        #total_vol=self.bases[self.bases['code']==code]['totals'].values[0]
        acutal_vol=self.bases[self.bases['code']==code]['outstanding'].values[0]
        all_vol= acutal_vol*cont
        #df= ts.get_hist_data(code)
        df1=ts.get_k_data(code)
        if len(df1)<3:
            return None
        #print df1.info()
        #df1=df.reset_index()
        #print df1
        start=df1['date'].values[0]
        print 'Start day:', start
        df2= df1[(df1['close']==df1['low']) & (df1['high']==df1['low'])]
        print self.bases[self.bases['code']==code]['name'].values[0]
        end=df2['date'].values[-1]
        print "Break day" , end

        df3=df1[(df1['date']>=start) & (df1['date']<=end)]
        v_total_break=df3['volume'].sum()
        print v_total_break
        rate=v_total_break*100*100.00/all_vol #手和股 注意
        print round(rate,6)





    def testcase(self):
        #self.calc_open_day('603096')
        for i in self.codes:
            self.calc_open_day(i)


def main():
    obj=New_Stock_Break()
    obj.testcase()
main()
