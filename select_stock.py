# -*-coding=utf-8-*-
__author__ = 'Rocky'
import tushare as ts
import pandas as pd
import os
#用来选股用的
pd.set_option('max_rows',None)
class select_class():
    def __init__(self):
        self.base=ts.get_stock_basics()
        #self.base.to_excel('111.xls',encoding='latin-1')

    def insert_garbe(self):
        print '*'*30
        print '\n'

    def showInfo(self,df=None):
        if df==None:
            df=self.base
        print '*'*30
        print '\n'
        print df.info()
        print '*'*30
        print '\n'
        print df.dtypes
        self.insert_garbe()

        print df.describe()

    #计算每个地区有多少上市公司
    def count_area(self,writeable=False):
        count=self.base['area'].value_counts()
        print count
        print type(count)
        if writeable:
            count.to_excel('each_area_stock.xls')

<<<<<<< HEAD
    #显示你要的某个省的上市公司
    def get_area(self,area,writeable=False):
        user_area=self.base[self.base['area']==area]
        if writeable:
            filename=area+'.xls'
            user_area.to_excel(filename)
        return user_area

    #显示次新股
    def cixingu(self,area,writeable=False):
        df=self.get_area(area)
        df_x=df.sort_values('timeToMarket',ascending=False)
        df_xx=df_x[:200]
        print df_xx
        if writeable:
            filename='cixin.xls'
            df_xx.to_excel(filename)
        #df_x= df.groupby('timeToMarket')
        #print df_x
        #df_x=df[df['timeToMarket']>'20170101']
        #print type( df['timeToMarket'])
        #df_time= df['timeToMarket']

        #new_df=pd.to_datetime(df_time)
        #print new_df
        #df_x= df[['area','timeToMarket']]
        #rint df_x.count()
    def output(self):
        print self.shenzhen()


if __name__=="__main__":
    currnet=os.getcwd()
    folder=os.path.join(currnet,'data')
    if os.path.exists(folder)==False:
        os.mkdir(folder)
    os.chdir(folder)
    obj=select_class()
    obj.cixingu('深圳',writeable=False)
    #obj.shenzhen()
    #obj.showInfo()
    #obj.count_area()
    #obj.get_area('河南')
=======
<<<<<<< HEAD:data/select_stock.py
        df_x=df.groupby('timeToMarket')
        print df_x
        for name,group in df_x:
            print name
            print group


=======
        #df_x=df[df['timeToMarket']>'20170101']
        #print type( df['timeToMarket'])
        df_time= df['timeToMarket']
        new_df=pd.to_datetime(df_time)
        print new_df
>>>>>>> origin/master:select_stock.py
    def output(self):
        print self.shenzhen()

obj=select_stocks()
obj.cixingu()
#obj.shenzhen()
>>>>>>> origin/master
