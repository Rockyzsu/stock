# -*-coding=utf-8-*-
__author__ = 'Rocky'
import tushare as ts
import pandas as pd
#用来选股用的

class select_stocks():
    def __init__(self):
        self.base=ts.get_stock_basics()

    def shenzhen(self):
        return self.base[self.base['area']=='深圳']

    def cixingu(self):
        df=self.shenzhen()

        #df_x=df[df['timeToMarket']>'20170101']
        #print type( df['timeToMarket'])
        df_time= df['timeToMarket']
        new_df=pd.to_datetime(df_time)
        print new_df
    def output(self):
        print self.shenzhen()

obj=select_stocks()
obj.cixingu()
#obj.shenzhen()