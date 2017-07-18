#-*-coding=utf-8-*-
#获取 不同形态的k线
import tushare as ts
import pandas as pd
import os,datetime,math
import numpy as np
pd.set_option('display.max_rows',None)
class kline():
    def __init__(self,cache=True):
        print 'tushare version: ', ts.__version__
        path=os.path.join(os.getcwd(),'data')
        self.today_date=datetime.datetime.now().strftime('%Y-%m-%d')
        print self.today_date
        if not os.path.exists(path) :
            os.mkdir(path)
        work_folder=os.chdir(path)

        #print self.all
        #self.today=ts.get_today_all()


        if cache:
            print 'Cache'
            self.today=pd.read_csv(self.today_date+'.csv',dtype={'code':np.str})
            self.all=pd.read_csv('bases.csv',dtype={'code': np.str})
        else:
            print 'Get from server'
            self.today=ts.get_today_all()
            self.today.to_csv(self.today_date+'.csv',encoding='gbk')
            self.all=ts.get_stock_basics()
            self.all.to_csv('bases.csv',encoding='gbk')

    def _xiayingxian(self,row):
        #print type(row)
        #print row
        open_p=row['open']
        #print open_p
        closed=row['trade']
        #print closed
        low=row['low']
        #print low
        settle=row['settlement']
        if open_p >=closed:
            try:
                diff=(closed-low)*1.00/settle*100
            except Exception,e:
                print e

            #print diff
            if diff>5:
                #print row['name'].decode('utf-8')
                print row['name'].decode('gbk')
                return row
        else:
            try:
                diff=(open_p-low)*1.00/settle*100
            except Exception,e:
                print e

            if diff>5:
                #print row['name'].decode('utf-8')
                print row['name'].decode('gbk')
                return row
    def xiayingxian(self):
        '''
        for i in self.today:
            print i
            #not each item
        '''
        lists=[]
        for i in range(len(self.today)):
            #print self.today[i]
            t=self._xiayingxian(self.today.loc[i])
            if t is not None:
                lists.append(t)
            #print i
        '''
        for i in lists:
            print type(i)
            print i
        '''
        result=pd.DataFrame(lists)
        print result
        return result

    def store_data(self):
        df=self.xiayingxian()
        df.to_csv('xiayinxian.csv')
if __name__=='__main__':
    obj=kline(cache=True)
    #obj.xiayingxian()
    obj.store_data()