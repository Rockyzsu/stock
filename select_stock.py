# -*-coding=utf-8-*-
__author__ = 'Rocky'
import tushare as ts
import pandas as pd
import os,sys,datetime,time
import numpy as np
reload(sys)
sys.setdefaultencoding('utf8')
#用来选股用的
#pd.set_option('max_rows',None)
#缺陷： 暂时不能保存为excel
class select_class():
    def __init__(self):
        #pass
        #self.bases=ts.get_stock_basics()

        #这里编码有问题
        #self.base.to_excel('base.xls',encoding='GBK')
        #self.base.to_excel('111.xls',encoding='utf8')
        #self.bases.to_csv('bases.csv')

        #因为网速问题，手动从本地抓取
        #self.base=pd.read_csv('bases.csv')
        self.base=pd.read_csv('bases.csv',dtype={'code':np.str})
        #print self.base
        #self.today=datetime.datetime.strftime('%Y-%m-%d')
        self.today = time.strftime("%Y-%m-%d", time.localtime())


    def insert_garbe(self):
        print '*'*30
        print '\n'

    def showInfo(self,df=None):
        if df==None:
            df=self.base
        print '*'*30
        print '\n'
        print df.info()
        print '*'*30
        print '\n'
        print df.dtypes
        self.insert_garbe()
        print df.describe()

    #计算每个地区有多少上市公司
    def count_area(self,writeable=False):
        count=self.base['area'].value_counts()
        print count
        print type(count)
        if writeable:
            count.to_csv(u'各省的上市公司数目.csv')
        return count


    #显示你要的某个省的上市公司
    def get_area(self,area,writeable=False):
        user_area=self.base[self.base['area']==area]
        user_area.sort_values('timeToMarket',inplace=True,ascending=False)
        if writeable:
            filename=area+'.csv'
            user_area.to_csv(filename)
        return user_area

    #显示次新股
    def cixingu(self,area,writeable=False):
        '''
        df=self.get_area(area)
        df_x=df.sort_values('timeToMarket',ascending=False)
        df_xx=df_x[:200]
        print df_xx
        if writeable:
            filename='cixin.csv'
            df_xx.to_csv(filename)
        '''
        #df_x= df.groupby('timeToMarket')
        #print df_x
        #df_x=df[df['timeToMarket']>'20170101']
        #print type( df['timeToMarket'])
        #df_time= df['timeToMarket']

        #new_df=pd.to_datetime(df_time)
        #print new_df
        #df_x= df[['area','timeToMarket']]
        #rint df_x.count()

        '''
        df_x=df.groupby('timeToMarket')
        print df_x
        for name,group in df_x:
            print name
            print group
        #df_x=df[df['timeToMarket']>'20170101']
        #print type( df['timeToMarket'])
        df_time= df['timeToMarket']
        new_df=pd.to_datetime(df_time)
        print new_df
        '''
        cixin=self.get_area(area).head(20)
        print cixin

    def output(self):
        print self.shenzhen()

    #获取所有地区的分类个股
    def get_all_location(self):
        series=self.count_area()
        index= series.index
        for i in index:
            name=unicode(i)
            self.get_area(name,writeable=True)

    #找出所有的次新股 默认12个月内
    def fetch_new_ipo(self,how_long=12,writeable=False):
            #需要继续转化为日期类型
            # date=
            df= self.base.loc[self.base['timeToMarket']>20160101]
            df.sort_values('timeToMarket',inplace=True,ascending=False)
            if writeable==True:
                df.to_csv("New_IPO.csv")
            return df

    #获取所有股票的代码
    def get_all_code(self):
            all_code=self.base['code'].values
            return all_code

    #计算一个票从最高位到目前 下跌多少
    def drop_down_from_high(self,start,code):

            end_day = datetime.date(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day)
            end_day = end_day.strftime("%Y-%m-%d")
            #print end_day
            #print start
            total=ts.get_k_data(code=code,start=start,end=end_day)
            #print total
            high=total['high'].max()
            high_day=total.loc[total['high']==high]['date'].values[0]

            print high
            print high_day
            current=total['close'].values[-1]
            print current
            percent=round((current-high)/high*100,2)
            print percent
            return percent

    def loop_each_cixin(self):
        df=self.fetch_new_ipo(writeable=True)
        all_code=df['code'].values
        print all_code
        #exit()
        percents=[]
        for each in all_code:
            print each
            #print type(each)
            percent=self.drop_down_from_high('2016-01-01',each)
            percents.append(percent)

        df['Drop_Down']=percents

        print df

        df.sort_values('Drop_Down',ascending=True,inplace=True)
        print df
        df.to_csv('drop_Down_cixin.csv')

    def get_macd(self,code):
        df=ts.get_k_data(code=code,start='2017-03-01')
        ma5= df['close'][-5:].mean()
        ma10= df['close'][-10:].mean()
        if ma5>ma10:
            print code

    #获取所有的ma5>ma10
    def macd(self):
        #df=self.fetch_new_ipo(writeable=True)
        #all_code=df['code'].values
        all_code=self.get_all_code()
        print all_code
        result=[]
        for each_code in all_code:
            df_x=ts.get_k_data(code=each_code,start='2017-03-01')
            #只找最近一个月的，所以no item的是停牌。
            if len(df_x)<11:
                #return
                print "no item"
                continue
            ma5= df_x['close'][-5:].mean()
            ma10= df_x['close'][-10:].mean()
            if ma5>ma10:

                #print "m5>m10: ",each_code," ",self.base[self.base['code']==each_code]['name'].values[0], "ma5: ",ma5,' m10: ',ma10
                temp=[each_code,self.base[self.base['code']==each_code]['name'].values[0]]
                print temp
                result.append(temp)
        print result
        print "Done"
        return result

    #写入csv文件
    def write_to_text(self):
        print "On write"
        r=self.macd()
        filename=self.today+"-macd.csv"
        f=open(filename,'w')
        for i in r:
            f.write(i[0])
            f.write(',')
            f.write(i[1])
            f.write('\n')
        f.close()
    #读取自己的csv文件
    def read_csv(self):
        filename=self.today+"-macd.csv"
        df=pd.read_csv(filename)
        print df
if __name__=="__main__":
    currnet=os.getcwd()
    folder=os.path.join(currnet,'data')
    if os.path.exists(folder)==False:
        os.mkdir(folder)
    os.chdir(folder)

    obj=select_class()
    #obj.cixingu('深圳',writeable=True)
    #obj.shenzhen()
    #obj.showInfo()
    #obj.count_area(writeable=True)
    #obj.get_area(u'广东',writeable=True)
    #obj.get_all_location()
    #obj.cixingu('上海')
    #obj.fetch_new_ipo(writeable=True)
    #obj.drop_down_from_high('2017-01-01','300580')
    #obj.loop_each_cixin()
    #obj.debug_case()
    #obj.get_macd()

    obj.write_to_text()
    #obj.read_csv()









