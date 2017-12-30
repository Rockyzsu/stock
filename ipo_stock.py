#-*-coding=utf-8-*-
import tushare as ts
import numpy as np
import datetime,os
import pandas as pd
import sys
from setting import get_engine
reload(sys)
sys.setdefaultencoding('utf8')
def ipo_rank():
    new_stk_df=ts.new_stocks()
    # print 'info',new_stk_df.info()
    # new_stk_df.dropna(inplace=True,axis=0)
    # print 'lens after drop ',len(new_stk_df)
    # new_stk_df['issue_date']=new_stk_df['issue_date'].astype('datetime64[ns]')
    new_stk_df['issue_date']=pd.to_datetime(new_stk_df['issue_date'])
    # new_stk_df['issue_date']=pd.to_datetime(new_stk_df['issue_date'])
    # new_stk_df=new_stk_df.set_index('issue_date')
    # print new_stk_df2.info()
    # print new_stk_df2
    # print new_stk_df2.truncate(after=date)
    # print new_stk_df2['2017-11-01':]
    # print len(new_stk_df)
    # print new_stk_df.head()
    # print new_stk_df.head()
    # print new_stk_df.info()
    df_2017 = new_stk_df[new_stk_df['issue_date']>'2017-01-01']
    # df_2017.to_excel('2017_new_stock.xls')
    # print new_stk_df.ix['2017-01-01':,:]
    pro=[]
    # print df_2017.iloc[0]['issue_date']
    # '''
    for i in range(len(df_2017)):
        s=df_2017.iloc[i]
        p=profit(s['code'],s['issue_date'].strftime('%Y-%m-%d'),'2017-12-29')
        pro.append(p)

    df_2017['raise']=pro

    df_2017.to_excel('2017newstockprofit.xls')
    # '''
def profit(code,start,end):
    # conn=ts.get_apis()
    try:
        # df=ts.bar(code,conn=conn,start_date=start,end_date=end)
        df=ts.get_k_data(code,start=start,end=end)
    except Exception,e:
        print e
        return None
    try:
        p=(df['close'].iloc[-1]-df['close'].iloc[0])/df['close'].iloc[0]*100.00
    except Exception,e:
        print e
        return None    
    
    # print p
    return round(p,2) 

def price_change():
    basic=ts.get_stock_basics()
    pro=[]
    print basic.info()
    print basic.head(10)

    # basic.to_csv('basic2017.xls',encoding='gbk')
    # df=pd.read_csv('basic2017.xls',encoding='gbk')
    # df.to_excel('basic2017.xls',encoding='gbk')

    # '''
    for code in basic.index.values:
        print code
        p=profit(code,'2016-12-31','2017-12-29')
        pro.append(p)
    basic['price_change']=pro
    basic.to_csv('2017_all_price_change.xls',encoding='gbk')
    df=pd.read_csv('2017_all_price_change.xls',encoding='gbk')
    df.to_excel('2017_all_price_change.xls',encoding='gbk')
    # basic.to_excel('2017_all_price_change.xls',encoding='utf-8')
    # '''

def analysis():
    df=pd.read_excel('2017_all_price_change.xls',encoding='gbk')
    # engine=get_engine('stock')
    # df.to_sql('2017yearsPriceChange',engine)
    # print df.head()
    # dfx = df[df['price_change'].notnull()]
    # new_df = dfx.sort_values(by='price_change')
    # print new_df[['code','name','industry','area','pe','timeToMarket','holders','price_change']].head(20)
    # print new_df[new_df.isnull()==True]
    # print new_df.loc[1242]
    # new_df=new_df.reset_index()
    # print len(new_df[new_df['price_change'].isnull()])
    # print dfx.tail(10)
    # print new_df.head(10)
    df=df.sort_values(by='price_change',ascending=False)
    # print df.head(5)
    df.to_excel('2017-year.xls',encoding='gbk')
def main():

    # ipo_rank()
    # price_change()
    analysis()

if __name__=='__main__':
    data_path=os.path.join(os.getcwd(),'data')
    os.chdir(data_path) 
    main()