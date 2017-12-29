#-*-coding=utf-8-*-
import tushare as ts
import numpy as np
import datetime,os
import pandas as pd

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
    for code in basic.index.values:
        print code
        p=profit(code,'2017-01-01','2017-12-29')
        pro.append(p)
    basic['price_change']=pro
    basic.to_excel('2017_all_price_change.xls',encoding='utf-8')


def main():
    # ipo_rank()
    price_change()

if __name__=='__main__':
    data_path=os.path.join(os.getcwd(),'data')
    os.chdir(data_path) 
    main()