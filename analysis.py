#-*-coding=utf-8-*-
'''
股票分析
'''
import datetime

from setting import get_engine
import pandas as pd
from scipy import stats

'''
今天涨跌幅的统计分析： 中位数，均值等数据
'''
def today_tendency(today):
    engine=get_engine('db_daily')
    today=datetime.datetime.strptime(today,'%Y%m%d').strftime('%Y-%m-%d')
    df = pd.read_sql(today,engine,index_col='index')
    # 去除停牌的 成交量=0
    df = df[df['volume']!=0]
    median = df['changepercent'].median()
    mean =  df['changepercent'].mean()
    std =  df['changepercent'].std()
    p_25=stats.scoreatpercentile(df['changepercent'],25)
    p_50=stats.scoreatpercentile(df['changepercent'],50)
    p_75=stats.scoreatpercentile(df['changepercent'],75)
    print u'中位数: {}'.format(median)
    print u'平均数: {}'.format(mean)
    print u'方差: {}'.format(std)
    print u'25%: {}'.format(p_25)
    print u'50%: {}'.format(p_50)
    print u'75%: {}'.format(p_75)

'''
分析昨天涨停的区域分布
'''
def yesterday_zt_location(date='20180404'):
    engine_zdt = get_engine('db_zdt')
    engine_basic = get_engine('db_stock')

    df = pd.read_sql(date+'zdt',engine_zdt,index_col='index')
    df_basic = pd.read_sql('basic_info',engine_basic,index_col='index')
    result={}
    for code in df[u'代码'].values:
        try:
            area=df_basic[df_basic['code']==code]['area'].values[0]
            result.setdefault(area,0)
            result[area]+=1

        except Exception,e:
            print e

    new_result = sorted(result.items(),key=lambda x:x[1],reverse=True)
    for k,v in  new_result:
        print k,v


def main():
    today=datetime.datetime.now().strftime("%Y%m%d")
    today_tendency(today)
    # yesterday_zt_location(today)

if __name__=='__main__':
    main()