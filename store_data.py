#-*-coding=utf-8-*-
__author__ = 'xda'
import tushare as ts
import sqlite3
class TS_DB():
    def __init__(self):
        self.db=sqlite3.connect("testdb.db")


    def save_csv(self,code):
        df = ts.get_k_data(code,start='2016-01-01',end='2016-12-28')
        filename=code+".csv"
        #df.to_csv(filename)
        df.to_sql("newtable",self.db,flavor='sqlite')


if __name__=="__main__":
    obj=TS_DB()
    obj.save_csv('300333')
