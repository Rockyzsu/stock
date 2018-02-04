# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
#交割单处理 保存交割单到数据库
import os,datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot  as plt
pd.set_option('display.max_rows',None)
class Delivery_Order():
    def __init__(self):
        print "Start"
        path=os.path.join(os.getcwd(),'data/2017/')
        if os.path.exists(path)==False:
            os.mkdir(path)
        os.chdir(path)

    #合并一年的交割单
    def years(self):
        df_list=[]
        k=[str(i) for i in range(1,13)]
        # print k
        j=[i for i in range(1,13)]
        result=[]
        for i in range(1,13):
            filename='2017-%s.xls' %str(i).zfill(2)
            #print filename
            t=pd.read_table(filename,encoding='gbk',dtype={u'证券代码':np.str})
            # fee=t[u'手续费'].sum()+t[u'印花税'].sum()+t[u'其他杂费'].sum()
            # print i," fee: "
            # print fee
            df_list.append(t)
            # result.append(fee)
        df=pd.concat(df_list)

        df[u'成交日期']=map(lambda x:datetime.datetime.strptime(str(x),"%Y%m%d"),df[u'成交日期'])
        df=df.sort_values(by=u'成交日期')
        df=df.set_index(u'成交日期')
        # print df.info()
        # print df
        # print df['2017-01']

        df=df[(df[u'摘要']==u'证券卖出') | (df[u'摘要']==u'证券买入')]
        # df= df.groupby(df[u'证券名称'])
        # print df.describe()
        # print df[u'手续费'].sum()
        # print df[u'印花税'].sum()
        df1=df[[u'证券名称',u'证券代码',u'成交数量',	u'成交均价'	,u'成交金额',u'手续费',	u'印花税',u'发生金额',u'操作']]
        # print df1[u'证券名称'].value_counts()
        print df.groupby(by=[u'证券名称'])[u'发生金额'].sum()
        # df1.to_excel('2017-all.xls')
        # print df1.groupby(df1[u'证券名称']).describe()
        # print df1['2017-02']
        #df.to_excel('2016_delivery_order.xls')
        # self.caculation(df)
        # plt.plot(j,result)
        # plt.show()

    def caculation(self,df):
        fee=df[u'手续费'].sum()+df[u'印花税'].sum()+df[u'其他杂费'].sum()
        print fee
    #计算每个月的费用
    def month(self):
        pass
def main():
    obj=Delivery_Order()
    obj.years()

main()


