#-*-coding=utf-8-*-
import tushare as ts
import os
cwd=os.getcwd()
os.chdir(os.path.join(cwd,'data'))

def main():
    df = ts.get_today_ticks('300104')
    total_vol=df['volume'].sum()*100
    print u'总成交股数'
    big_deal=df[df['volume']>=100]['volume'].sum()*100
    print u'大于100手的总和',big_deal
    percent=float(big_deal)/total_vol*100
    print u'大单占比',percent
    print df['volume'].value_count()


if __name__ == '__main__':
    main()