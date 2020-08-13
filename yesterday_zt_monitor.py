# -*-coding=utf-8-*-
import datetime
import os
import matplotlib
'''
昨日涨停的今日的实时情况
'''
matplotlib.use("Pdf")
from settings import DBSelector, is_holiday, DATA_PATH
import pandas as pd
import tushare as ts
import numpy as np
from plot_line import plot_stock_line
from settings import llogger

logger = llogger('log/yester_zdt.log')
DB = DBSelector()

def monitor():
    engine = DB.get_engine('db_zdt','qq')
    table = '20180409zdt'
    api = ts.get_apis()
    df = pd.read_sql(table, engine, index_col='index')
    price_list = []
    percent_list = []
    amplitude_list = []
    start = datetime.datetime.now()
    for i in df['代码'].values:
        try:
            curr = ts.quotes(i, conn=api)
            last_close = curr['last_close'].values[0]
            curr_price = curr['price'].values[0]
            amplitude = round(((curr['high'].values[0] - curr['low'].values[0]) * 1.00 / last_close) * 100, 2)
            # if last_close>=curr_price:
            # print(i,)
            # print(df[df['代码']==i]['名称'].values[0],)
            # print( percent)
        except Exception as e:
            print('this point')
            print(e)
            api=ts.get_apis()
            curr_price = 0

        if last_close == 0:
            percent = np.nan
        percent = round((curr_price - last_close) * 100.00 / last_close, 2)
        percent_list.append(percent)
        price_list.append(curr_price)
        amplitude_list.append(amplitude)

    df['今日价格'] = price_list
    df['今日涨幅'] = percent_list
    df['今日振幅'] = amplitude_list
    df['更新时间'] = datetime.datetime.now().strftime('%Y %m %d %H:%M%S')

    end = datetime.datetime.now()
    print('time use {}'.format(end - start))

    df.to_sql(table + 'monitor', engine, if_exists='replace')
    ts.close_apis(api)


'''
绘制k线图，今日涨停的k线图
'''


def plot_yesterday_zt(type_name='zrzt', current=datetime.datetime.now().strftime('%Y%m%d')):
    engine = DB.get_engine('db_zdt','qq')
    table_name = type_name
    table = '{}{}'.format(current, table_name)
    try:
        df = pd.read_sql(table, engine)
    except Exception as e:
        logger.error('table_name >>> {}{}'.format(current,table_name))
        logger.error(e)
        return
    start_data = datetime.datetime.now() + datetime.timedelta(days=-200)
    start_data=start_data.strftime('%Y-%m-%d')
    for i in range(len(df)):
        code = df.iloc[i]['代码']
        name = df.iloc[i]['名称']

        plot_stock_line(api,code, name, table_name=table_name, current=current, start=start_data, save=True)


if __name__ == '__main__':

    if is_holiday():
        logger.info('Holiday')
        exit()

    logger.info("Start")
    api = ts.get_apis()
    # current='20191016'
    current = datetime.datetime.now().strftime('%Y%m%d')
    data_path = DATA_PATH

    path = os.path.join(DATA_PATH, current)
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)

    for plot_type in ['zrzt', 'zdt']:
        try:
            plot_yesterday_zt(plot_type, current=current)
        except Exception as e:
            logger.error(e)
            continue
    ts.close_apis(api)