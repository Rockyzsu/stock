# -*- coding: utf-8 -*-
# @Time : 2021/4/2 18:08
# @File : TushareUtil.py
# @Author : Rocky C@www.30daydo.com
import tushare as ts
import sys

sys.path.append('..')
from configure.settings import config
from datetime import datetime
import time


class TushareBaseUtil:
    '''
    tushare 常用调用
    '''

    def __init__(self):
        ts_token = config.get('ts_token')
        ts.set_token(ts_token)
        self.pro = ts.pro_api()
        self.cache = {}

    def get_trade_date(self, start_date=None, end_date=datetime.now().strftime('%Y%m%d')):
        '''
        返回交易日历
        :param start_date:
        :param end_date:
        :return:
        '''
        # if self.cache
        if 'cal_date' not in self.cache:
            df = self.pro.trade_cal(exchange='', is_open='1', start_date=start_date, end_date=end_date)
            self.cache['cal_date'] = df['cal_date'].tolist()
        return self.cache['cal_date']

    def date_convertor(self, s):
        return datetime.strptime(s, '%Y%m%d').strftime('%Y-%m-%d')

    def get_last_trade_date(self):
        return self.get_trade_date()[-2]

    def get_last_week_trade_date(self):
        return self.get_trade_date()[-5]

    def clear_cache(self):
        self.cache = {}


def main():
    # today =datetime.now().strftime('%Y%m%d')
    app = TushareBaseUtil()
    df = app.get_trade_date()
    df = app.get_trade_date()
    df = app.get_trade_date()
    df = app.get_trade_date()
    d = app.get_last_trade_date()
    print(d)


if __name__ == '__main__':
    start = time.time()
    main()
    print(f'time used {time.time() - start}')
