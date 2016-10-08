# -*-coding=utf-8-*-
#记录每天选股后的收益，用于跟踪每一只自选股
__author__ = 'Rocky'
import datetime,os,xlrd,time
from xlutils.copy import copy
import tushare as ts

class Prediction_rate():

    def __init__(self):
        self.today_stock=ts.get_today_all()
        now=datetime.datetime.now()
        self.today=now.strftime("%Y-%m-%d")
        #weekday=now+datetime.timedelta(days=-2)
        #weekday=weekday.strftime("%Y-%m-%d")
        #print weekday
        #today=now.strftime('%Y-%m-%d')
        self.path=os.path.join(os.getcwd(),'data')
        self.filename=os.path.join(self.path,'recordMyChoice.xls')

    def stock_pool(self,stock_list):


    def first_record(self,stockID):
        #stockID_list=['000673']

        wb=xlrd.open_workbook(self.filename)
        table=wb.sheets()[0]
        nrow=table.nrows
        ncol=table.ncols
        print "%d*%d" %(nrow,ncol)
        row_start=nrow
        wb_copy=copy(wb)
        sheet=wb_copy.get_sheet(0)
        #调用 write 函数写入 info write(1,1,'Hello')

        content=[]
        mystock=self.today_stock[self.today_stock['code']==stockID]
        name=mystock['name'].values[0]
        in_price=mystock['trade'].values[0]
        current_price=in_price
        profit=0.0
        content=[self.today,stockID,name,in_price,current_price,profit]

        for i in range(len(content)):
            sheet.write(row_start,i,content[i])

        row_start=row_start+1

        wb_copy.save(self.filename)

    def update(self):
        #对已有的进行更新
        pass


if __name__ == "__main__":
    obj=Prediction_rate()
    obj.first_recode()
