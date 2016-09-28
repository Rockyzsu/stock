# -*-coding=utf-8-*-
#练习tushare

import tushare as ts
import sys
import numpy as np
import pandas as pd
import time


class StockBox:
    def __init__(self, date=time.strftime("%Y-%m-%d")):
        self.date = date


    def base_function(self, id):
        if id == None:
            print "Input stock id please "
            return

        stockInfo = ts.get_hist_data(id)
        # print type(stockInfo)
        # print stockInfo.head()
        # print stockInfo.dtypes
        df = ts.get_stock_basics()
        data = df.ix[id]['timeToMarket']
        print data
        all_data = ts.get_today_all()
        print all_data.ix[id]['name']

    def realtime(self, id):
        # all_stock=ts.get_today_all()
        # print all_stock
        df = ts.get_realtime_quotes(id)
        # print df[['time','name','price','bid','ask','volume']]
        # print df.head()
        # price_change = ts.get_today_ticks(id)
        # print price_change[['time','change','type','volume']]
        big_share = ts.get_sina_dd(id, date=self.date)
        print big_share[['time', 'code', 'price', 'preprice', 'volume', 'type']]
        print big_share.sort(columns='volume')

    def looper(self, id):
        while (1):
            self.realtime(id)
            time.sleep(30)

    def getNews(self):
        token = '60517739976b768e07823056c6f9cb0fee33ed55a1709b3eaa14a76c6a1b7a56'
        ts.set_token(token)
        print ts.get_token()
        mkt = ts.Market()
        df = mkt.TickRTSnapshot(securityID='000001.XSHE')
        print df

    def longhuban(self, date):
        print ts.top_list(date)
        print ts.cap_tops()

    def get_stock_chengfeng(self):
        df = ts.get_sz50s()
        # print df
        terminal_stock = ts.get_terminated()
        print terminal_stock

    def fund(self):
        fd = ts.Fund()
        df = fd.FundDiv(ticker='184688', adjustedType='D', beginDate='20000101',
                        field='secShortName,effectDate,publishDate,dividendAfTax,dividendBfTax')
        print df
        dd = ts.fund_holdings(2015, 4)
        print dd[['name', 'nums', 'clast', 'amount']]


    def date_store(self):
        df = ts.get_hist_data("300333")
        # df.to_csv("300333.cvs")
        df.to_excel("300333.xlsx")

    def profit_test(self):
        df = ts.profit_data(top=60)
        print df.sort_value(by='shares', ascending=False)

    def longhubang(self):

        df = ts.broker_tops(days=5)
        df_save = df.sort_values(by='count', ascending=False)
        df_save.to_excel("longhubang-10day.xlsx")


    '''
    Keep on this
    '''

    def daily_longhu(self):
        # date=self.date
        date = '2016-04-05'
        df = ts.top_list(date)
        df.to_excel(date + ".xlsx")


def main():
    now = time.strftime("%Y-%m-%d")
    # print now
    token = '60517739976b768e07823056c6f9cb0fee33ed55a1709b3eaa14a76c6a1b7a56'
    sb = StockBox()
    # sb.looper(id)
    id = '300333'
    # sb.realtime(id)
    sb.base_function("300333")
    # pandas_test=Pandas_test()
    # pandas_test.test_function()
    # sb.longhuban('2016-04-05')
    # sb.getNews()
    # sb.fund()
    #sb.get_stock_chengfeng()
    #sb.date_store()
    #sb.profit_test()
    #sb.daily_longhu()


    # 获取历史数据 近3年的数据
    history = ts.get_hist_data(id)

    print u"历史3年的数据"

    print history.head(10)

    history_all = ts.get_h_data(id, '20015101', '20160101')

    print u'所有的历史数据'
    print history_all



    # print type(stockInfo)
    # print stockInfo.head()
    # print stockInfo.dtypes
    #df = ts.get_stock_basics()
    #data = df.ix[id]['timeToMarket']
    #print data
    #ts.get_today_all()


def get_info(self, id):
    # 获取一些股票的基本信息
    df = ts.get_stock_basics()
    print df.ix['300333']['timeToMarket']


def realtime(self, id):
    # all_stock=ts.get_today_all()
    # print all_stock
    df = ts.get_realtime_quotes(id)
    # print df[['time','name','price','bid','ask','volume']]
    # print df.head()

    price_change = ts.get_today_ticks(id)
    print price_change[['time', 'change', 'type', 'volume']]
    big_share = ts.get_sina_dd(id, date='2016-04-01')
    print big_share[['time', 'code', 'price', 'preprice', 'volume', 'type']]


def looper(self, id):
    while (1):
        self.realtime(id)
        time.sleep(30)


def getNews(self):
    token = '60517739976b768e07823056c6f9cb0fee33ed55a1709b3eaa14a76c6a1b7a56'
    ts.set_token(token)
    print ts.get_token()
    mkt = ts.Market()
    df = mkt.TickRTSnapshot(securityID='000001.XSHE')
    print df


def longhuban(self, date):
    print ts.top_list(date)
    print ts.cap_tops()


def get_stock_chengfeng(self):
    df = ts.get_sz50s()
    # print df
    terminal_stock = ts.get_terminated()
    print terminal_stock


def fund(self):
    fd = ts.Fund()
    df = fd.FundDiv(ticker='184688', adjustedType='D', beginDate='20000101',
                    field='secShortName,effectDate,publishDate,dividendAfTax,dividendBfTax')
    print df
    dd = ts.fund_holdings(2015, 4)
    print dd[['name', 'nums', 'clast', 'amount']]


def main():
    # 获取历史数据 近3年的数据
    history = ts.get_hist_data(id)

    print u"历史3年的数据"

    print history.head(10)

    history_all = ts.get_h_data(id, '20015101', '20160101')

    print u'所有的历史数据'
    print history_all



    # print type(stockInfo)
    # print stockInfo.head()
    # print stockInfo.dtypes
    # df = ts.get_stock_basics()
    #data = df.ix[id]['timeToMarket']
    #print data
    #ts.get_today_all()


def get_info(self, id):
    # 获取一些股票的基本信息
    df = ts.get_stock_basics()
    print df.ix['300333']['timeToMarket']


def realtime(self, id):
    # all_stock=ts.get_today_all()
    # print all_stock
    df = ts.get_realtime_quotes(id)
    # print df[['time','name','price','bid','ask','volume']]
    # print df.head()

    price_change = ts.get_today_ticks(id)
    print price_change[['time', 'change', 'type', 'volume']]
    big_share = ts.get_sina_dd(id, date='2016-04-01')
    print big_share[['time', 'code', 'price', 'preprice', 'volume', 'type']]


def looper(self, id):
    while (1):
        self.realtime(id)
        time.sleep(30)


def getNews(self):
    token = '60517739976b768e07823056c6f9cb0fee33ed55a1709b3eaa14a76c6a1b7a56'
    ts.set_token(token)
    print ts.get_token()
    mkt = ts.Market()
    df = mkt.TickRTSnapshot(securityID='000001.XSHE')
    print df


def longhuban(self, date):
    print ts.top_list(date)
    print ts.cap_tops()


def get_stock_chengfeng(self):
    df = ts.get_sz50s()
    # print df
    terminal_stock = ts.get_terminated()
    print terminal_stock


def fund(self):
    fd = ts.Fund()
    df = fd.FundDiv(ticker='184688', adjustedType='D', beginDate='20000101',
                    field='secShortName,effectDate,publishDate,dividendAfTax,dividendBfTax')
    print df
    dd = ts.fund_holdings(2015, 4)
    print dd[['name', 'nums', 'clast', 'amount']]


'''
def main():

    token = '60517739976b768e07823056c6f9cb0fee33ed55a1709b3eaa14a76c6a1b7a56'
    id = '300333'
    # id=sys.argv[1]

    sb = StockBox()

    # sb.base_function(id)
    sb.get_info(id)


    #sb.base_function(id)
    sb.get_info(id)
'''

# sb.looper(id)
# sb.realtime(id)
# stockBox.base_function("300333")
# pandas_test=Pandas_test()
# pandas_test.test_function()
# sb.longhuban('2016-04-05')
# sb.getNews()
# sb.fund()
# sb.get_stock_chengfeng()



class Pandas_test:
    def test_function(self):
        dates = pd.date_range("20160501", periods=10)
        print dates


if __name__ == "__main__":
    main()
