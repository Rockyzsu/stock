'''
@author:rocky
@email:weigesysu@qq.com
@feature: 收盘事后分析
'''

from configure.settings import DBSelector
import pandas as pd
from scipy import stats
import tushare as ts
import datetime
import os
# import matplotlib.pyplot as plt
import numpy as np

pd.set_option('display.max_rows', None)


def volume_calculation(code, start, end):
    '''
    计算某个股票的某个时间段的累计成交量

    :param start: 开始日期
    :param end: 结束日期
    :return: 成交量，占每天比例
    '''

    df = ts.get_today_ticks(code)

    # 转换str为时间格式，便于下面用来比较时间的大小
    df['time'] = df['time'].map(lambda x: datetime.datetime.strptime(str(x), '%H:%M:%S'))
    total = df['volume'].sum()
    start = datetime.datetime.strptime(start, '%H:%M:%S')
    end = datetime.datetime.strptime(end, '%H:%M:%S')
    new_df = df[(df['time'] >= start) & (df['time'] < end)]

    volume = new_df['volume'].sum()
    rate = round(volume * 1.00 / total * 100, 2)

    return volume, rate


def today_statistics(today):
    '''
    :help: 今天涨跌幅的统计分析： 中位数，均值等数据
    :param today: 日期 2019-01-01
    :return:None
    '''

    engine = DBSelector().get_engine('db_daily')
    df = pd.read_sql(today, engine, index_col='index')
    # 去除停牌的 成交量=0

    df = df[df['volume'] != 0]
    median = round(df['changepercent'].median(), 2)
    mean = round(df['changepercent'].mean(), 2)
    std = round(df['changepercent'].std(), 2)
    p_25 = round(stats.scoreatpercentile(df['changepercent'], 25), 2)
    p_50 = round(stats.scoreatpercentile(df['changepercent'], 50), 2)
    p_75 = round(stats.scoreatpercentile(df['changepercent'], 75), 2)

    print('中位数: {}'.format(median))
    print('平均数: {}'.format(mean))
    print('方差: {}'.format(std))
    print('25%: {}'.format(p_25))
    print('50%: {}'.format(p_50))
    print('75%: {}'.format(p_75))


def zt_location(date):
    '''
    :help: 分析涨停的区域分布
    :param date:日期格式 20180404
    :return:
    '''
    engine_zdt = DBSelector().get_engine('db_zdt')
    engine_basic = DBSelector().get_engine('db_stock')

    df = pd.read_sql(date + 'zdt', engine_zdt, index_col='index')
    df_basic = pd.read_sql('tb_basic_info', engine_basic, index_col='index')
    result = {}

    for code in df['代码'].values:
        try:
            area = df_basic[df_basic['code'] == code]['area'].values[0]
            result.setdefault(area, 0)
            result[area] += 1

        except Exception as e:
            print(e)

    new_result = sorted(result.items(), key=lambda x: x[1], reverse=True)
    for k, v in new_result:
        print(k, v)


def show_percentage(price):
    '''
    :help: 根据收盘价计算每个百分比的价格
    :param open_price: 开盘价
    :return:
    '''

    for i in range(1, 11):
        print('{}\t+{}% -> {}'.format(price, i, round(price * (1 + 0.01 * i), 2)))

    for i in range(1, 11):
        print('{}\t-{}% -> {}'.format(price, i, round(price * (1 - 0.01 * i), 2)))


def stock_profit(code, start, end):
    '''
    :help: 计算某个时间段的收益率
    :param code: 股票代码
    :param start: 开始时间
    :param end: 结束时间
    :return: 收益率
    '''

    k_data = ts.get_k_data(start=start, end=end, code=code)

    if len(k_data)==0:
        return np.nan

    start_price = k_data['close'].values[0]
    print("Start price: ", start_price)

    end_price = k_data['close'].values[-1]

    print("End price: ", end_price)

    earn_profit = (end_price - start_price) / start_price * 100
    print("Profit: ", round(earn_profit, 2))
    return round(earn_profit, 2)


def exclude_kcb(df):
    '''
    :help: 去除科创板
    :param df:
    :return:
    '''
    non_kcb = df[~df['code'].map(lambda x: True if x.startswith('688') else False)]
    return non_kcb


def plot_percent_distribution(date):
    '''
    :help:图形显示某一天的涨跌幅分布
    :param date:
    :return:
    '''
    import matplotlib.pyplot as plt

    total = []
    engine = DBSelector().get_engine('db_daily')
    df = pd.read_sql(date, con=engine)
    df = exclude_kcb(df)

    count = len(df[(df['changepercent'] >= -11) & (df['changepercent'] <= -9.5)])
    total.append(count)

    for i in range(-9, 9, 1):
        count = len(df[(df['changepercent'] >= i * 1.00) & (df['changepercent'] < ((i + 1)) * 1.00)])
        total.append(count)

    count = len(df[(df['changepercent'] >= 9)])
    total.append(count)
    # print(total)
    df_figure = pd.Series(total)
    plt.figure(figsize=(16, 10))
    X = range(-10, 10)
    plt.bar(X, height=total, color='y')
    for x, y in zip(X, total):
        plt.text(x, y + 0.05, y, ha='center', va='bottom')
    plt.grid()
    plt.xticks(range(-10, 11))
    plt.show()


def year_price_change(year,ignore_new_stock=False):
    '''
    :year: 年份
    :ignore_new_stock: 排除当年上市的新股
    计算某年个股的涨幅排名
    :return: None 生成excel
    '''

    year = int(year)

    basic = ts.get_stock_basics()
    pro = []

    name=''
    # basic['timeToMarket']=pd.to_datetime(basic['timeToMarket'],format='%Y%m%d')

    # 去除当年的新股
    if ignore_new_stock:
        basic=basic[basic['timeToMarket']< int('{}0101'.format(year))]
        name = '_ignore_new_stock'

    filename='{}_all_price_change{}.xls'.format(year,name)

    for code in basic.index.values:
        p = stock_profit(code, '{}-01-01'.format(year), '{}-01-01'.format(year+1))
        pro.append(p)

    basic['p_change_year'] = pro
    basic=basic.sort_values(by='p_change_year', ascending=False)
    basic.to_excel(filename, encoding='gbk')


def stock_analysis(filename):
    '''
    # 分析年度的数据
    :return:
    '''

    df=pd.read_excel(filename,encoding='gbk')
    print('mean:\n',df['p_change_year'].mean())
    print('max:\n',df['p_change_year'].max())
    print('min:\n',df['p_change_year'].min())
    print('middle\n',df['p_change_year'].median())
    # plt.figure()
    # df['p_change_year'].plot.hist()
    # plt.show()


def cb_stock_year():
    '''
    上一年可转债正股的涨跌幅排名
    :return:
    '''
    engine = get_engine('db_stock')
    df_cb = pd.read_sql('tb_bond_jisilu', engine)
    filename='2019_all_price_change_ignore_new_stock.xls'
    df_all=pd.read_excel(filename,encoding='gbk')
    zg_codes = list(df_cb['正股代码'].values)
    df = df_all[df_all['code'].isin(zg_codes)]
    df.to_excel('2019_cb_zg.xls',encoding='gbk')

def main():
    ## 某个股票某个时间段的成交量 ####
    # code = '000069'
    # v, ratio = volume_calculation(code,'09:30:00', '10:00:00')
    # print('\n')
    # print(v, ratio)

    ## 涨跌幅分布 #####
    # TODAY=datetime.datetime.now().strftime("%Y-%m-%d")
    # today_tendency(TODAY)

    ## 分析涨停的区域分布 ####
    # TODAY = datetime.datetime.now().strftime("%Y%m%d")
    # zt_location(TODAY)

    ## 显示百分比价格
    # show_percentage(121)

    ## 计算某个个股某段时间的收益率
    # stock_profit('300333','2019-01-01','2020-02-03')

    ## 显示价格分布
    # date = '2020-02-07'
    # plot_percent_distribution(date)

    # 某年个股涨幅
    # year_price_change(2019,True)
    # stock_analysis('2019_all_price_change_ignore_new_stock.xls')

    cb_stock_year()

if __name__ == '__main__':
    main()
