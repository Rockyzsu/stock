# -*-coding=utf-8-*-
import time

__author__ = 'rocky'
# 获取破指定天数内的新高 比如破60日新高
import tushare as ts
import datetime
import pandas as pd
from configure.settings import DBSelector,_json_data
import pymongo
from config import token
# from filter_stock import Filter_Stock

db = DBSelector()
INFO = _json_data['mongo']['arm']
host = INFO['host']
port = INFO['port']
user = INFO['user']
password = INFO['password']

class BreakPoint(object):

    def __init__(self):
        self.engine = db.get_engine('db_stock', 'qq')
        self.conn = db.get_mysql_conn('db_stock', 'qq')
        self.info = pd.read_sql('tb_basic_info', con=self.engine, index_col='code')
        connect_uri = f'mongodb://{user}:{password}@{host}:{port}'
        self.db = pymongo.MongoClient(connect_uri)
        self.doc = self.db['db_stock']['break_low_high']
        ts.set_token(token)
        self.pro = ts.pro_api()
        self.count = 0

    # 获取新高，新低
    def loop_stocks(self, day):
        total = 200 + 10
        each_loop = 60 / total
        for idx, row in self.info.iterrows():
            stock_code = idx
            print('Checking {}'.format(stock_code))
            self.is_break(stock_code, day, stock_type='stock')
            time.sleep(each_loop)

    def code_convert(self, code):
        if code[0] == '6':
            return code + '.SH'
        else:
            return code + '.SZ'

    def is_break(self, stockID, day, stock_type):

        end_day = datetime.datetime.now()
        days = day * 7 / 5
        # 考虑到周六日非交易
        start_day = end_day - datetime.timedelta(days)

        start_day = start_day.strftime("%Y%m%d")
        end_day = end_day.strftime("%Y%m%d")
        name = self.info.ix[stockID]['name']
        # get_h_data 有问题。

        try:

            # df = ts.get_k_data(stockID, start=start_day, end=end_day)
            ts_code = self.code_convert(stockID)
            df = ts.pro_bar(ts_code=ts_code, adj='qfq', start_date=start_day, end_date=end_day)
            # df 第0个数据是最新的。

        except Exception as e:
            print(e)
            print('{} {}获取行情识别'.format(stockID, name))
            time.sleep(30)

            return False

        if df is None or df.empty:
            print('{} {} df is None or empty'.format(stockID, name))
            return False

        if len(df) < 5:
            print('上市时间太短'.format(stockID, name))
            return False

        period_high = df['close'][1:].max()
        today_high = df.iloc[0]['high']

        if today_high >= period_high:
            stock_h = []

            stock_h.append(stockID)
            stock_h.append(name)
            insert_dict = {'类型': '新高', '范围': days, '名称': name, '代码': stockID, 'run_time': datetime.datetime.now(),
                           '品种': stock_type, '开始日期': start_day, '结束日期': end_day}
            self.doc.insert_one(insert_dict)

        period_low = df['close'][1:].min()
        today_low = df.iloc[0]['low']

        if today_low <= period_low:
            stock_l = []

            name = self.info.ix[stockID]['name']
            stock_l.append(stockID)
            stock_l.append(name)
            print('新低', stock_l)
            insert_dict = {'类型': '新低', '范围': days, '名称': name, '代码': stockID, 'run_time': datetime.datetime.now(),
                           '品种': stock_type, '开始日期': start_day, '结束日期': end_day}
            self.doc.insert_one(insert_dict)


if __name__ == '__main__':
    obj = BreakPoint()
    cal_day = 90
    obj.loop_stocks(cal_day)
    print("Done")
