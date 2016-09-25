# -*-coding=utf-8-*-
#数据库的操作

import sqlite3, time, datetime,os

__author__ = 'rocky'


class SqliteDb():


    def __init__(self,dbname):
        '''
        self.today = time.strftime("%Y-%m-%d")
        self.DBname = self.today + '.db'
        self.conn = sqlite3.connect(self.DBname)
        '''
        today = time.strftime("_%Y_%m_%d")
        path=os.path.join(os.getcwd(),'data')
        self.DBname =  os.path.join(path,dbname+ '.db')
        self.conn = sqlite3.connect(self.DBname)
        self.dbtable=today
        create_tb = "CREATE TABLE %s (date varchar(10),id varchar(6), name varchar(30), p_change REAL,turnover REAL);" %self.dbtable
        self.conn.execute(create_tb)
        self.conn.commit()

    def store_break(self,price_data):

        #data 是创新高(低)的个股信息  dataframe
        #print today
        #create_tb = 'CREATE TABLE STOCK (date TEXT,id text PRIMARY KEY, p_change REAL,turnover REAL);'

        #conn.commit()
        #print "(%s,%s,%f,%f)" %(price_high_data[0], price_high_data[1], price_high_data[2], price_high_data[3])
        insert_data_cmd = "INSERT INTO %s(date,id,name,p_change,turnover) VALUES(\"%s\",\"%s\",\"%s\",%f,%f);" %(self.dbtable,price_data[0], price_data[1], price_data[2], price_data[3],price_data[4])
        self.conn.execute(insert_data_cmd)
        #self.conn.execute('INSERT INTO STOCK(date,id,name,p_change,turnover) VALUES(?,?,?,?,?)',(price_high_data[0], price_high_data[1], price_high_data[2], price_high_data[3],price_high_data[4]))
        self.conn.commit()


    def close(self):
        self.conn.close()