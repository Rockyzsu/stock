#-*-coding=utf-8-*-
__author__ = 'xda'
import tushare as ts

class TS_DB():

    def save_csv(self,code):
        df = ts.get_k_data(code,start='2016-01-01',end='2016-12-28')
        filename=code+".csv"
        df.to_csv(filename)



if __name__=="__main__":
    obj=TS_DB()
    obj.save_csv('300333')
