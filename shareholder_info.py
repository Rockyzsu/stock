# -*- coding: utf-8 -*-
# @Time : 2019/1/19 14:37
# @File : stockholder_info.py
# 股东信息获取
import re
import sys
import pandas as pd
import time
import traceback
from configure.settings import DBSelector
from common.Base import pro
import json


class ShareHolderInfo():
    '''
    十大股东与十大流通股东
    '''
    def __init__(self):
        self.init_mongo()
        self.tushare_init()

    def db_init(self):
        self.conn = DBSelector().get_mysql_conn('db_stock')
        self.cursor = self.conn.cursor()

    def init_mongo(self):
        self.client = DBSelector().mongo('qq')
        self.doc_holder = self.client['db_stock']['shareHolder']  # 十大
        self.doc_holder_float = self.client['db_stock']['shareHolder_float']  # 十大

    def tushare_init(self):
        self.pro = pro

    def exists(self, code):
        result = self.doc_holder.find_one({'ts_code': code})
        return False if result is None else True

    def get_stock_list(self, exchange):
        df = self.pro.stock_basic(exchange=exchange, list_status='L')
        return dict(zip(list(df['ts_code'].values), list(df['name'].values)))

    # 生产日期 2000到2018
    @staticmethod
    def create_date():
        start_date = '20{}0101'
        end_date = '20{}1231'
        date_list = []
        for i in range(18, 0, -1):
            print(start_date.format(str(i).zfill(2)))
            print(end_date.format(str(i).zfill(2)))
            date_list.append(i)
        return date_list

    # 十大和十大流通
    def get_stockholder(self, code, start, end):
        '''
        stockholder 十大
        stockfloat 十大流通
        '''
        try:
            stockholder = self.pro.top10_holders(ts_code=code, start_date=start, end_date=end)
            # time.sleep(1)
            stockfloat = self.pro.top10_floatholders(ts_code=code, start_date=start, end_date=end)
            # time.sleep(1)

        except Exception as e:
            print(e)
            time.sleep(10)
            # ts.set_token(config['ts_token'])
            self.pro = pro
            stockholder = self.pro.top10_holders(ts_code=code, start_date=start, end_date=end)
            # time.sleep(1)
            stockfloat = self.pro.top10_floatholders(ts_code=code, start_date=start, end_date=end)
            # time.sleep(1)
        else:
            if stockholder.empty or stockfloat.empty:
                print('有空数据----> ', code)
                return pd.DataFrame(), pd.DataFrame()

            else:
                return stockholder, stockfloat

    def dumpMongo(self, doc, df):
        record_list = df.to_json(orient='records', force_ascii=False)
        record_list = json.loads(record_list)
        if len(record_list)==0:
            return
        try:
            doc.insert_many(record_list)
        except Exception as e:
            exc_type, exc_value, exc_obj = sys.exc_info()
            traceback.print_exc()

    def valid_code(self, code):
        return True if re.search('^\d{6}\.\S{2}', code) else False

    def run(self):
        start_date = '20{}0101'
        end_date = '20{}1231'
        exchange_list = ['SSE', 'SZSE']
        for ex in exchange_list:
            code_dict = self.get_stock_list(ex)
            for code, name in code_dict.items():
                # for i in range(20, 0, -1):
                i = 21
                if not self.valid_code(code):
                    print('invalid code ', code)
                    continue

                if self.exists(code):
                    continue

                print('crawling -->', code)

                start = start_date.format(str(i).zfill(2))
                end = end_date.format(str(i).zfill(2))
                df_holding, df_float = self.get_stockholder(code, start, end)
                self.dumpMongo(self.doc_holder, df_holding)
                self.dumpMongo(self.doc_holder_float, df_float)
                time.sleep(0.1)


def main():
    app = ShareHolderInfo()
    app.run()


if __name__ == '__main__':
    main()
