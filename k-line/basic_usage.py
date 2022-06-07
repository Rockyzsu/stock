import akshare as ak
import mpl_finance as mpf
import matplotlib.pyplot as plt
import pandas as pd


def get_k_data(code="sz123073",name="同和转债k.xlsx"):
    df = ak.stock_zh_a_daily(symbol=code, start_date="20200901", end_date="20201230",
                                                          adjust="qfq")
    df.to_excel(name)



def kline_demo():
    #创建绘图的基本参数
    fig=plt.figure(figsize=(12, 8))
    ax=fig.add_subplot(111)

    #获取刚才的股票数据
    df = pd.read_excel("同和药业k.xlsx")
    mpf.candlestick2_ochl(ax, df["open"], df["close"], df["high"], df["low"], width=0.6, colorup='r',colordown='green',alpha=1.0)
    #显示出来
    plt.show()

def axis_date():
    from datetime import datetime
    from matplotlib.pylab import date2num
    import matplotlib.ticker as ticker
    #将股票时间转换为标准时间，不带时分秒的数据
    def date_to_num(dates):
        num_time = []
        for date in dates:
            date_time = datetime.strptime(date, '%Y-%m-%d')
            num_date = date2num(date_time)
            num_time.append(num_date)
        return num_time

    #创建绘图的基本参数
    fig=plt.figure(figsize=(12, 8))
    ax=fig.add_subplot(111)

    #获取刚才的股票数据
    df = pd.read_excel("同和药业k.xlsx")
    mpf.candlestick2_ochl(ax, df["open"], df["close"], df["high"], df["low"], width=0.6, colorup='r',colordown='green',alpha=1.0)
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    def format_date(x, pos=None):
        if x < 0 or x > len(df['date']) - 1:
            return ''
        return df['date'][int(x)]
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    #显示出来
    plt.show()


def ma_line():

    from datetime import datetime
    from matplotlib.pylab import date2num
    import matplotlib.ticker as ticker
    import numpy as np
    #将股票时间转换为标准时间，不带时分秒的数据
    def date_to_num(dates):
        num_time = []
        for date in dates:
            date_time = datetime.strptime(date, '%Y-%m-%d')
            num_date = date2num(date_time)
            num_time.append(num_date)
        return num_time

    #创建绘图的基本参数
    fig=plt.figure(figsize=(12, 8))
    ax=fig.add_subplot(111)

    #获取刚才的股票数据
    df = pd.read_excel("同和药业k.xlsx")
    mpf.candlestick2_ochl(ax, df["open"], df["close"], df["high"], df["low"], width=0.6, colorup='r',colordown='green',alpha=1.0)
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    df["SMA5"] = df["close"].rolling(5).mean()
    df["SMA10"] = df["close"].rolling(10).mean()
    df["SMA30"] = df["close"].rolling(30).mean()

    ax.plot(np.arange(0, len(df)), df['SMA5'])  # 绘制5日均线
    ax.plot(np.arange(0, len(df)), df['SMA10'])  # 绘制10日均线
    ax.plot(np.arange(0, len(df)), df['SMA30'])  # 绘制30日均线

    def format_date(x, pos=None):
        if x < 0 or x > len(df['date']) - 1:
            return ''
        return df['date'][int(x)]
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    #显示出来
    plt.show()




def add_vol():
    # 加入成交量
    import mpl_finance as mpf
    import matplotlib.pyplot as plt
    import pandas as pd
    import matplotlib.ticker as ticker
    import numpy as np
    # 创建绘图的基本参数
    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(15, 10))
    ax1, ax2 = axes.flatten()

    # 获取刚才的股票数据
    df = pd.read_excel("同和药业k.xlsx")
    mpf.candlestick2_ochl(ax1, df["open"], df["close"], df["high"], df["low"], width=0.6, colorup='r',
                          colordown='green', alpha=1.0)
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))

    def format_date(x, pos=None):
        if x < 0 or x > len(df['date']) - 1:
            return ''
        return df['date'][int(x)]

    df["SMA5"] = df["close"].rolling(5).mean()
    df["SMA10"] = df["close"].rolling(10).mean()
    df["SMA30"] = df["close"].rolling(30).mean()
    ax1.plot(np.arange(0, len(df)), df['SMA5'])  # 绘制5日均线
    ax1.plot(np.arange(0, len(df)), df['SMA10'])  # 绘制10日均线
    ax1.plot(np.arange(0, len(df)), df['SMA30'])  # 绘制30日均线
    ax1.grid(True)
    ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    red_pred = np.where(df["close"] > df["open"], df["volume"], 0)
    blue_pred = np.where(df["close"] < df["open"], df["volume"], 0)
    ax2.bar(np.arange(0, len(df)), red_pred, facecolor="red")
    ax2.bar(np.arange(0, len(df)), blue_pred, facecolor="green")
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    # 显示出来
    plt.grid(visible=True)



    plt.show()


def long_up_shadow(o,c,h,l):
    return True if (h-c)/c >=0.07 and (h-o)/o>=0.07 else False

from recognize_form import plot_image
def run():
    df = pd.read_excel("同和药业k.xlsx")
    count_num = []
    for row,item in df.iterrows():
        if long_up_shadow(item['open'],item['close'],item['high'],item['low']):
            count_num.append(row)

    plot_image(df,count_num)