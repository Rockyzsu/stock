# -*-coding=utf-8-*-
__author__ = 'Rocky'
import tushare as ts

#用来选股用的

class select_stocks():
    def __init__(self):
        self.base=ts.get_stock_basics()

    def shenzhen(self):
        return self.base[self.base['area']=='深圳']

    def cixingu(self):
        df=self.shenzhen()

        #df_x=df[df['timeToMarket']>'20170101']
        print type( df['timeToMarket'])

    def output(self):
        print self.shenzhen()
obj=select_stocks()
obj.cixingu()