# -*-coding=utf-8-*-
import sys

__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
#计算股价涨跌幅
import tushare as ts
class calculator_stock():

    #date= YYYY-MM-DD
    def profit(self,start,end,code):


        start_price=ts.get_k_data(start=start,end=start,code=code)
        if len(start_price)==0:
            print "Not open for start day"
            #采用日期操作，往前移动上一个开盘日.
        s_price=start_price['close'].values[0]
        print "Start price: ",s_price

        end_price=ts.get_k_data(start=end,end=end,code=code)

        if len(end_price)==0:
            print "Not open for end day"

        e_price=end_price['close'].values[0]
        print "End price: ",e_price
        earn_profit=(e_price-s_price)/s_price*100
        print "Profit: ",
        print round(earn_profit,2)

def percentage(open_price):
    open_price=float(open_price)
    for i in range(1,11):
        print '{}\t+{}%->{}'.format(open_price,i,open_price*(1+0.01*i))
    for i in range(1,11):
        print '{}\t-{}%->{}'.format(open_price,i,open_price*(1-0.01*i))

if __name__=="__main__":
    ''''
    obj=calculator_stock()

    code='300333'
    start='2015-12-21'
    end='2017-04-14'

    obj.profit(start,end,code)
    '''
    #percentage(sys.args[1])
    percentage(24.54)