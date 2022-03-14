# -*- coding: utf-8 -*-
# @Time : 2021/8/24 6:06
# @File : fund_jsl.py
# @Author : Rocky C@www.30daydo.com


import random
import re
import datetime
import demjson
import requests
import time
import sys

sys.path.append('..')
from configure.settings import DBSelector
from common.BaseService import BaseService
# from configure.util import notify
import warnings

warnings.filterwarnings("ignore")

now = datetime.datetime.now()
TODAY = now.strftime('%Y-%m-%d')
_time = now.strftime('%H:%M:%S')

if _time < '11:30:00':
    TODAY += 'morning'
elif _time < '14:45:00':
    TODAY += 'noon'
else:
    TODAY += 'close'
    # TODAY += 'noon' # 调试

NOTIFY_HOUR = 13
MAX_PAGE = 50

try:
    DB = DBSelector()
    conn = DB.get_mysql_conn('db_fund', 'qq')
    cursor = conn.cursor()
except Exception as e:
    print(e)

'''
集思录部分代码
'''


class JSLFund(BaseService):
    '''
    集思录的指数
    '''

    def __init__(self):
        super(JSLFund, self).__init__(f'../log/{self.__class__.__name__}.log')

        client = DB.mongo(location_type='qq', async_type=False)

        self.jsl_stock_lof = client['fund_daily'][f'jsl_stock_lof_{self.today}']
        self.jsl_index_lof = client['fund_daily'][f'jsl_index_lof_{self.today}']

        self.stock_url = 'https://www.jisilu.cn/data/lof/stock_lof_list/?___jsl=LST___t=1582355333844&rp=25'
        self.index_lof_url = 'https://www.jisilu.cn/data/lof/index_lof_list/?___jsl=LST___t=1582356112906&rp=25'
        self.logger.info(f'start JSL fund...')

    @property
    def headers(self):
        _headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}
        return _headers

    def get(self, url, retry=5):

        start = 0
        while start < retry:
            try:
                r = requests.get(
                    url=url,
                    headers=self.headers)
            except Exception as e:
                self.logger.error(e)
                start += 1

            else:
                js = r.json()
                return js

        if start == retry:
            return None

    def crawl(self):
        for types in ['stock', 'index']:
            self.parse_json(types=types)

    def parse_json(self, types):

        if types == 'stock':
            url = self.stock_url
            mongo_doc = self.jsl_stock_lof

        else:
            url = self.index_lof_url
            mongo_doc = self.jsl_index_lof

        return_js = self.get(url=url)
        rows = return_js.get('rows')

        for item in rows:
            cell = item.get('cell')
            cell['crawltime'] = datetime.datetime.now()
            try:
                mongo_doc.insert_one(cell)
            except Exception as e:
                self.logger.error(e)
                self.notify(title=f'{self.__class__} 写入mongodb出错')


def main():
    pass


if __name__ == '__main__':
    main()
