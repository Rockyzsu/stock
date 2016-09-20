# -*-coding=utf-8-*-
__author__ = 'Rocky'
import tushare as ts
import time,datetime,os,xlrd,xlwt
class Candle_Stick():

    def __init__(self):
        self.baseinfo=ts.get_stock_basics()
        self.getDate()
        self.today_all=ts.get_today_all()

    def getDate(self):
        self.now=datetime.datetime.now()
        self.today=self.now.strftime('%Y-%m-%d')
        self.yesterday=self.now+datetime.timedelta(days=-1)
        self.yesterday=self.yesterday.strftime('%Y-%m-%d')
        self.before_yesterday=self.now+datetime.timedelta(days=-2)
        self.before_yesterday=self.before_yesterday.strftime('%Y-%m-%d')
        '''
        print self.today
        print self.yesterday
        print self.before_yesterday
        '''

    def getHistory(self,id):
        data=ts.get_hist_data(id)
        print data

    def isFileExist(self,filename):
        if not os.path.exists(filename):
            excel_file=xlwt.Workbook()
            sheet=excel_file.add_sheet('2016-09')
            data=[u'买入日期',u'代码',u'名称',u'买入价',u'今天价格',u'今天涨幅',u'截止今天的收益']
            row=0
            for col in range(len(data)):
                sheet.write(row,col,data[col])
            excel_file.save(filename)


    def my_choice(self,id):

        #pd=ts.get_hist_data(code=id,start=self.yesterday,end=self.today,retry_count=5)
        close_price= self.today_all.ix[id][id]
        name=self.today_all.ix[id]['name']
        changepercent=self.today_all.ix[id]['changepercent']
        trade=self.today_all.ix[id]['trade']
        #print pd
        data=[self.today,id,name,trade,changepercent]
        print data
        for i in data:
            print i

if __name__=="__main__":
    obj=Candle_Stick()
    #obj.getHistory('300333')
    #obj.isFileExist('candle.xls')
    obj.my_choice('300333')