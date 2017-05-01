# -*-coding=utf-8-*-
__author__ = 'Rocky'
#查看ipo速度 和指数的关系
import tushare as ts
#import  datetime
from datetime import datetime
import pandas as pd
import numpy as np
from pandas import Series
import matplotlib.pyplot as plt
pd.set_option('display.max_rows',None)
class IPO_Speed():

    def __init__(self):
        self.ipo=ts.new_stocks()
        #print ipo.info()

        #日期转化
        self.ipo['ipo_date']=self.ipo['ipo_date'].astype('datetime64')
        #print ipo.info()
        self.start=self.ipo['ipo_date'].values[-1]
        self.end=self.ipo['ipo_date'].values[0]
        print type(self.end)
        #转化类型
        #ipo['ipo_date']=ipo['ipo_date'].astype('datetime64')
        #self.start_d=datetime.datetime.strptime(self.start,'%Y-%m-%d')
        #self.end_d=datetime.datetime.strptime(self.end,'%Y-%m-%d')
        #print type(self.start_d)
        #period=self.start_d+datetime.timedelta(days=30)
        #print period.strftime('%Y-%m-%d')
        #print ipo[ipo['ipo_date']<np.datetime64(period)]



    def comparation(self):
        #print self.start
        #print self.end
        delta=30
        count_list=[]
        profit_list=[]
        self.period=self.end+np.timedelta64(delta,'D')
        #print self.period
        #print self.ipo[self.ipo['ipo_date']<self.period]
        #print type(self.end.tolist())
        l= self.end.tolist()
        ns=1e-9
        b= datetime.utcfromtimestamp(l * ns)
        #print datetime.fromtimestamp(self.end.tolist())
        c= b.strftime('%Y-%m-%d')
        #print type(c)
        start_data=self.start
        while start_data < self.end:
            #print start_data
            first_date=start_data
            start_data=start_data+np.timedelta64(delta,'D')
            result=self.ipo[(self.ipo['ipo_date']>=first_date) &(self.ipo['ipo_date']<start_data)]
            #print result
            count=len(result)

            temp_end_data=start_data+np.timedelta64(-1,'D')
            t=pd.to_datetime(str(temp_end_data))
            d=t.strftime('%Y-%m-%d')
            print d
            t1=pd.to_datetime(str(first_date))
            d1=t1.strftime('%Y-%m-%d')
            print d1
            sz_index_data=ts.get_k_data('399001',index=True,start=d1,end=d)
            #print index_data
            #大盘（深圳，考虑到国家队在上证的操作） 在30天内的收益
            before=sz_index_data['close'].values[0]
            after=sz_index_data['close'].values[-1]
            #profit_index=(index_data['close'][-1]-index_data['close'][0])/index_data['close'][0]*100
            p=round((after-before)/before*100,2)
            print p
            print count
            count_list.append(count)
            profit_list.append(p)

        return count_list,profit_list


    def draw(self):
        count,profit=self.comparation()
        s1=Series(count,index=range(len(count)))
        s2=Series(profit,index=range(len(profit)))
        '''
        ax=s1.plot()
        ax2=s2.plot()
        fig=ax.get_figure()
        fig.savefig('count.png')
        fig2=ax2.get_figure()
        fig2.savefig('profit.png')
        '''
        r=s1.corr(s2)
        print r





def main():
    obj=IPO_Speed()
    obj.draw()

main()