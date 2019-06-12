# -*-coding=utf-8-*-
__author__ = 'rocky'
# 获取破指定天数内的新高 比如破60日新高
import tushare as ts
import datetime
import pandas as pd
from setting import get_engine, get_mysql_conn
import pymongo

MONGO_HOST = '10.18.6.46'
MONGO_PORT = 27001


class BreakPoin(object):

    def __init__(self):
        self.engine = get_engine('db_stock', local=True)
        self.conn = get_mysql_conn('db_stock', local='local')
        self.info = pd.read_sql('tb_basic_info', con=self.engine, index_col='code')
        self.db = pymongo.MongoClient(MONGO_HOST, MONGO_PORT)
        self.doc = self.db['db_stock']['break_low_high']

    def loop_stocks(self):

        for idx, row in self.info.iterrows():
            stock_code = idx
            self.is_break(stock_code, 90, break_type='high', stock_type='stock')
            self.is_break(stock_code, 90, break_type='low', stock_type='stock')

    def is_break(self, stockID, days, break_type, stock_type):

        end_day = datetime.datetime.now()
        days = days * 7 / 5
        # 考虑到周六日非交易
        start_day = end_day - datetime.timedelta(days)

        start_day = start_day.strftime("%Y-%m-%d")
        end_day = end_day.strftime("%Y-%m-%d")
        name = self.info.ix[stockID]['name']
        # get_h_data 有问题。

        try:

            df = ts.get_k_data(stockID, start=start_day, end=end_day)

        except Exception as e:
            print(e)
            print('{} {}获取行情识别'.format(stockID, name))
            return False

        if df is None or df.empty:
            print('{} {} df is None or empty'.format(stockID, name))
            return False

        if len(df) < 5:
            print('上市时间太短'.format(stockID, name))
            return False

        if break_type == 'high':

            period_high = df['high'][:-1].max()
            today_high = df.iloc[-1]['high']
            # 这里不能直接用 .values
            # 如果用的df【：1】 就需要用.values
            # print(today_high)

            if today_high >= period_high:

                stock_h = []

                stock_h.append(stockID)
                stock_h.append(name)
                insert_dict = {'类型': '新高', '范围': days, '名称': name, '代码': stockID, 'date': datetime.datetime.now(),
                               '品种': stock_type}
                self.doc.insert_one(insert_dict)
                return True

            else:

                return False

        elif break_type == 'low':

            period_low = df['low'][:-1].min()
            today_low = df.iloc[-1]['low']

            if today_low <= period_low:

                stock_l = []

                name = self.info.ix[stockID]['name']
                stock_l.append(stockID)
                stock_l.append(name)
                print('新低', stock_l)
                insert_dict = {'类型': '新低', '范围': days, '名称': name, '代码': stockID, 'date': datetime.datetime.now(),
                               '品种': stock_type}
                self.doc.insert_one(insert_dict)

                return True

            else:
                return False


if __name__ == '__main__':
    obj = BreakPoin()
    obj.loop_stocks()
    print("Done")
