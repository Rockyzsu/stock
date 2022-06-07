import pandas as pd
import talib
import sys

import tushare as ts
sys.path.append('..')
from configure.settings import config_dict
ts_token = config_dict('ts_token')
ts.set_token(ts_token)
pro = ts.pro_api()
start_date='20220105'
end_date='20220520'


import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import mpl_finance as mpf

def plot(df):
    fig = plt.figure(figsize=(12, 8))
    plt.rcParams['font.sans-serif'] = ['SimHei']
    ax = fig.add_subplot(111)

    # df['trade_date'] = df['trade_date'].apply(lambda x: x.strftime('%Y%m%d'))
    df['tow_crows'] = talib.CDL2CROWS(df['open'].values, df['high'].values, df['low'].values, df['close'].values)

    pattern = df[(df['tow_crows'] == 100) | (df['tow_crows'] == -100)]
    mpf.candlestick2_ochl(ax, df["open"], df["close"], df["high"], df["low"], width=0.6, colorup='r',
                          colordown='green',
                          alpha=1.0)
    for index, today in pattern.iterrows():
        x_posit = df.index.get_loc(index)
        s = "{}\n{}".format("两只乌鸦", today["trade_date"])
        ax.annotate(s, xy=(x_posit, today["high"]),
                    xytext=(0, pattern["close"].mean()), xycoords="data",
                    fontsize=18, textcoords="offset points", arrowprops=dict(arrowstyle="simple", color="r"))

    ax.xaxis.set_major_locator(ticker.MaxNLocator(20))

    def format_date(x, pos=None):
        if x < 0 or x > len(df['trade_date']) - 1:
            return ''
        return df['trade_date'][int(x)]

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
    plt.show()

def get_all_codes():
    df = pro.stock_basic(exchange='', list_status='', fields='')
    return df['ts_code'].tolist()

def get_daily(code):
    df = pro.daily(ts_code=code, start_date=start_date, end_date=end_date)
    return df

def search(df):
    # df['date'] = pd.to_datetime(df['date'])
    # df['date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
    if len(df)==0:
        return False,[]
    df['tow_crows'] = talib.CDL2CROWS(df['open'].values, df['high'].values, df['low'].values, df['close'].values)
    pattern = df[(df['tow_crows'] == 100) | (df['tow_crows'] == -100)]
    if len(pattern)>0:
        location = []
        for index, today in pattern.iterrows():
            x_posit = df.index.get_loc(index)
            location.append(x_posit)
        return True,location
    return False,[]



def run():
    code_list = get_all_codes()
    for code in code_list:
        df = get_daily(code)
        found,location=search(df)
        if found:
            print(code,df.loc[location])
            plot(df)


run()
