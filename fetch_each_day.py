# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
#get top 50 turnover ratio stocks
import tushare as ts
import pandas as pd
import time,datetime,os,xlrd,xlwt
from sqlalchemy import create_engine
from toolkit import Toolkit
class Fetch_each_day():

    def __init__(self):
        #self.baseinfo=ts.get_stock_basics()
        self.getDate()
        self.path=os.path.join(os.path.dirname(__file__),'data')

        self.df_today_all=pd.DataFrame()

    def excel_operation(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        self.GetAllTodayData()
        self.sortTurnOver()

    def getDate(self):
        #获取当前3天内的日期，后面会进行是否为开盘日的判断
        self.now=datetime.datetime.now()
        self.today=self.now.strftime('%Y-%m-%d')
        self.yesterday=self.now+datetime.timedelta(days=-1)
        self.yesterday=self.yesterday.strftime('%Y-%m-%d')
        self.before_yesterday=self.now+datetime.timedelta(days=-2)
        self.before_yesterday=self.before_yesterday.strftime('%Y-%m-%d')

    def GetAllTodayData(self):
        #存储每天 涨幅排行  榜,避免每次读取耗时过长
        filename=self.today+'_all_.xls'
        #放在data文件夹下
        filename=os.path.join(self.path,filename)
        if not os.path.exists(filename):
            re_try=5
            while re_try>0:
                try:
                    self.df_today_all=ts.get_today_all()
                #过滤停牌的
                # self.df_today_all.drop(self.df_today_all[self.df_today_all['turnoverratio']==0].index,inplace=True)
                #实测可用，删除的方法
                #n1=self.df_today_all[self.df_today_all['turnoverratio']==0]
                #n2=self.df_today_all.drop(n1.index)
                #print n2
                # print self.df_today_all
                    if len(self.df_today_all)!=0:
                        break
                except Exception,e:
                    re_try=re_try-1
                    time.sleep(5)
            if len(self.df_today_all)!=0:

                self.df_today_all.to_excel(filename,sheet_name='All')
            else:
                self.df_today_all=None
        else:
            self.df_today_all=pd.read_excel(filename,sheet_name='All')
            # print "File existed"
        return self.df_today_all

    def sortTurnOver(self):
        top_filename=self.today+'_top_turnover.xls'
        topfile=os.path.join(self.path,top_filename)
        if not os.path.exists(topfile):
            high_turnover=self.df_today_all.sort_values(by='turnoverratio',ascending=False)
            top_high=high_turnover.head(100)

            top_high.to_excel(topfile,sheet_name='heat100')
            return top_high
        else:
            df=pd.read_excel(topfile,sheetname='heat100')
            return df

    def getHistory(self,id):
        data=ts.get_hist_data(id)
        print data

    def isFileExist(self,filename):
        if not os.path.exists(filename):
            excel_file=xlwt.Workbook()
            sheet=excel_file.add_sheet('2016-09')
            data=[u'买入日期',u'代码',u'名称',u'买入价',u'今天价格',u'今天涨幅',u'换手率',u'截止今天的收益']
            row=0
            for col in range(len(data)):
                sheet.write(row,col,data[col])
            excel_file.save(filename)
        else:
            print "File existed"

    def save_sql(self):
        cfg_file=os.path.join(os.path.dirname(__file__),'data.cfg')
        data=Toolkit.getUserData(cfg_file)
        sql_pwd=data['MYSQL_PASSWORD']
        self.engine=create_engine('mysql+pymysql://root:%s@localhost/db_daily?charset=utf8' %sql_pwd)

        # self.df_today_all=ts.get_today_all()
        self.df_today_all['turnoverratio']=map(lambda x:round(x,2),self.df_today_all['turnoverratio'])
        self.df_today_all['per']=map(lambda x:round(x,2),self.df_today_all['per'])
        self.df_today_all['pb']=map(lambda x:round(x,2),self.df_today_all['pb'])
        self.df_today_all.to_sql(self.today,self.engine,if_exists='replace')


if __name__=="__main__":
    obj=Fetch_each_day()
    #obj.getHistory('300333')
    #obj.isFileExist('candle.xls')
    #obj.my_choice('300333')
    obj.excel_operation()
    obj.save_sql()
