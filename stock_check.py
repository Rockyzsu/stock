# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
#查询个股
import tushare as ts
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
class CheckStock():
    def __init__(self):
        #self.id=id
        pass
        '''
        if len(self.id)!=6:
            print "Wrong stock code"
            exit()
        '''


    def multi_thread(self):

        with open('stock_list.txt') as f:
            stock_list=f.readlines()

        ratio_list=[]
        for i in stock_list:
            i=i.strip()
            ratio_list.append(self.get_info(i))
        print ratio_list
        return ratio_list

    def get_info(self,id):
        print id
        try:
            df=ts.get_today_ticks(id)
            print 'len of df ',len(df)
            print df
            if len(df)==0:
                print "Pause of exchange"
                return
        except Exception,e:
            print e
            print "ERROR"

        print '\n'
        max_p=df['price'].max()
        print max_p
        min_p=df['price'].min()
        print min_p
        #print df
        buy= df[df['type']==u'买盘']['volume'].sum()
        print 'buy:',buy
        sell =df[df['type']==u'卖盘']['volume'].sum()
        print 'sell: ',sell
        neutral= df[df['type']==u'中性盘']['volume'].sum()
        print 'neutral: ',neutral
        #最后一个是开盘数据
        start=df[-1:]
        vol_0=start['volume'].sum()
        print 'start'
        print start
        total=buy+sell+neutral+vol_0

        sum_all=df['volume'].sum()

        print total
        print sum_all

        ratio=round((buy-sell)*1.00/sell*100,2)
        print "buy/sell ratio: ",ratio
        return id,ratio
        '''
        df['price'].plot()
        plt.grid()

        plt.show()
        '''

    def show_name(self):
        #self.all=ts.get_stock_basics()
        self.bases_save=ts.get_stock_basics()

        self.bases_save.to_csv('bases.csv')
        self.base = pd.read_csv('bases.csv', dtype={'code': np.str})
        stock_list=self.multi_thread()
        for st in stock_list:

            print "code: ",st[0]
            name=self.base[self.base['code']==st[0]]['name']
            print 'name: ',name
            print "ratio: ",st[1]
if __name__=="__main__":
    obj=CheckStock()
    #obj.get_info('000693')
    #obj.multi_thread()
    obj.show_name()