#-*-coding=utf-8-*-
'''
股票分析
'''
from setting import get_engine
import pandas as pd
from scipy import stats
def today_tendency():
    engine=get_engine('db_daily')
    today='2018-03-23'
    df = pd.read_sql(today,engine,index_col='index')
    median = df['changepercent'].median()
    mean =  df['changepercent'].mean()
    std =  df['changepercent'].std()
    # mean =  df['changepercent'].mean()
    # mean =  df['changepercent'].mean()
    # mean =  df['changepercent'].mean()
    p_25=stats.scoreatpercentile(df['changepercent'],25)
    p_50=stats.scoreatpercentile(df['changepercent'],50)
    print u'中位数:{}'.format(median)
    print u'平均数:{}'.format(mean)
    print u'方差:{}'.format(std)
    print u'平均数:{}'.format(mean)
    print u'25%:{}'.format(p_25)
    print u'50%:{}'.format(p_50)
    # print u'平均数:{}'.format(mean)
    p50_1=df['changepercent'].quantile(0.25)
    print u'another 50%:{}'.format(p50_1)


if __name__=='__main__':
    today_tendency()