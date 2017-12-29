#-*-coding=utf-8-*-
import tushare as ts
import numpy as np
import datetime
def ipo_rank(date):
    new_stk_df=ts.new_stocks()
    new_stk_df.dropna(inplace=True,axis=0)
    print len(new_stk_df)
    new_stk_df['issue_date']=new_stk_df['issue_date'].astype('datetime64[ns]')
    new_stk_df=new_stk_df.set_index('issue_date')
    print new_stk_df.info()
    new_stk_df=new_stk_df.truncate(after=datetime.datetime(2017,01,01))
    print len(new_stk_df)
    print new_stk_df.head()

def main():
    ipo_rank('2017-01-01')

if __name__ == '__main__':
    main()