# 识别k线形态

import pandas as pd
import talib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mpl_finance as mpf

def two_crow():
    fig = plt.figure(figsize=(12, 8))
    plt.rcParams['font.sans-serif'] = ['SimHei']
    ax = fig.add_subplot(111)
    df = pd.read_excel("歌尔股份2020.xlsx")
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    df['tow_crows'] = talib.CDL2CROWS(df['open'].values, df['high'].values, df['low'].values, df['close'].values)

    pattern = df[(df['tow_crows'] == 100) | (df['tow_crows'] == -100)]

    mpf.candlestick2_ochl(ax, df["open"], df["close"], df["high"], df["low"], width=0.6, colorup='r',
                              colordown='green',
                              alpha=1.0)
    for index, today in pattern.iterrows():
        x_posit = df.index.get_loc(index)
        s="{}\n{}".format("两只乌鸦", today["date"])
        ax.annotate(s, xy=(x_posit, today["high"]),
                    xytext=(0, pattern["close"].mean()), xycoords="data",
                    fontsize=18, textcoords="offset points", arrowprops=dict(arrowstyle="simple", color="r"))


    ax.xaxis.set_major_locator(ticker.MaxNLocator(20))

    def format_date(x, pos=None):
        if x < 0 or x > len(df['date']) - 1:
            return ''
        return df['date'][int(x)]


    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.show()

def plot_image(df,target):
    fig = plt.figure(figsize=(12, 8))
    plt.rcParams['font.sans-serif'] = ['SimHei']
    ax = fig.add_subplot(111)
    df['date'] = pd.to_datetime(df['date'])
    df['date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    mpf.candlestick2_ochl(ax, df["open"], df["close"], df["high"], df["low"], width=0.6, colorup='r',
                          colordown='green',
                          alpha=1.0)
    for index in target:
        x_posit = df.index.get_loc(index)
        s = "{}\n{}".format("长上影", df.loc[index]["date"][5:])
        ax.annotate(s, xy=(x_posit, df.loc[index]["high"]),
                    xytext=(0, df.loc[index]["close"].mean()), xycoords="data",
                    fontsize=18, textcoords="offset points", arrowprops=dict(arrowstyle="simple", color="r"))

    ax.xaxis.set_major_locator(ticker.MaxNLocator(20))

    def format_date(x, pos=None):
        if x < 0 or x > len(df['date']) - 1:
            return ''
        return df['date'][int(x)]
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

    plt.show()