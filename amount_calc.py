# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
#计算某个股票的某个时间段的成交量
import  tushare as ts
import pandas as pd
import datetime
pd.set_option('display.max_rows',None)
class amount_calculation():
    def __init__(self,code):
        self.df=ts.get_today_ticks(code)

        #转换str为时间格式，便于下面用来比较时间的大小
        self.df['time']=self.df['time'].map(lambda x:datetime.datetime.strptime(str(x),'%H:%M:%S'))
        print '\n'
        self.total= self.df['volume'].sum()

    def calc(self,start,end):
        s0=datetime.datetime.strptime(start,'%H:%M:%S')
        e0=datetime.datetime.strptime(end,'%H:%M:%S')
        new_df=self.df[(self.df['time']>=s0) & (self.df['time']<e0) ]
        #print new_df
        part= new_df['volume'].sum()
        rate=round(part*1.00/self.total*100,2)
        print part
        print rate
        return rate




def main():
    obj=amount_calculation('300023')
    #s1=obj.calc('09:24:00','10:30:00')
    #s2=obj.calc('10:30:00','11:30:00')
    #s3=obj.calc('13:00:00','14:00:00')
    s4=obj.calc('09:30:00','09:47:00')
    #print s1+s2+s3+s4

main()








