# -*-coding=utf-8-*-
__author__ = 'Rocky'
#模拟买入 纯粹纪录。
import os,sys,chardet
import pandas,datetime
import numpy as np
import tushare as ts
class simulation_buy():

    def __init__(self):
        path=os.path.join(os.getcwd(),'data')
        if os.path.exists(path)==False:
            os.mkdir(path)
        os.chdir(path)
        self.name='simulation.xls'
        self.df=pandas.read_excel(self.name)
        self.df[u'代码']=self.df[u'代码'].map(lambda x:str(x).zfill(6))
        self.base=pandas.read_csv('bases.csv',dtype={'code':np.str})
        self.money=10000
        print self.df
        self.today=datetime.datetime.now().strftime('%Y-%m-%d')
        print self.today

    def caculation(self):
            df_t=ts.get_today_all()
            print self.df[u'代码'].values
            for i in self.df[u'代码'].values:
                name=self.base[self.base['code']==i]['name'].values[0]
                print name
                t=name.decode('utf-8')
                print
                print type(t)
                #print chardet.detect(t)
                self.df.ix[self.df[u'代码']==i,u'当前日期']=self.today
                #t=ts.get_k_data(i)

                pchange=df_t.ix[df_t['code']==i,'changepercent'].values[0]
                print pchange
                self.df.ix[self.df[u'代码']==i,u'今日涨幅']=pchange
                current=df_t[df_t['code']==i]['trade'].values[0]
                self.df.ix[self.df[u'代码']==i,u'当前价格']=current
                current_profit=(current-self.df[self.df[u'代码']==i][u'买入价格'].values[0])/self.df[self.df[u'代码']==i][u'买入价格'].values[0]
                self.df.ix[self.df[u'代码']==i,u'目前盈亏']=round(current_profit*100,2)
                print current_profit
            print self.df
            self.df.to_excel(self.name,encoding='utf-8')

def main():
    obj=simulation_buy()
    obj.caculation()


if __name__=='__main__':
    main()


