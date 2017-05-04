# -*-coding=utf-8-*-
__author__ = 'Rocky'
#交割单处理
import os,datetime
import pandas as pd
import numpy as np
pd.set_option('display.max_rows',None)
class Delivery_Order():
    def __init__(self):
        print "Start"
        path=os.path.join(os.getcwd(),'data')
        if os.path.exists(path)==False:
            os.mkdir(path)
        os.chdir(path)

    #合并一年的交割单
    def years(self):
        df_list=[]
        k=[str(i) for i in range(1,13)]
        print k
        for i in range(1,13):
            filename='2016-%s.xls' %str(i).zfill(2)
            print filename
            t=pd.read_table(filename,encoding='gbk',dtype={u'证券代码':np.str})
            df_list.append(t)
        df=pd.concat(df_list,keys=k)
        print df
        #df.to_excel('2016_delivery_order.xls')
        self.caculation(df)

    def caculation(self,df):
        fee=df[u'手续费'].sum()+df[u'印花税'].sum()+df[u'其他杂费'].sum()
        print fee


def main():
    obj=Delivery_Order()
    obj.years()

main()


