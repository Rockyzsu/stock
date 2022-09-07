# -*-coding=utf-8-*-
# @Time : 2018/8/7 13:45
# @File : foreignexchange.py
# 实时获取外汇

import re
import datetime
import requests
import sys
sys.path.append('..')

from common.BaseService import BaseService
from configure.util import send_message_via_wechat
from configure.settings import DBSelector

# 失效
class ForeighExchange(BaseService):

    def __init__(self):
        super(ForeighExchange, self).__init__('log/usd.log')
        self.url = 'http://data.bank.hexun.com/other/cms/foreignexchangejson.ashx?callback=ShowDatalist'
        self.update_req = 10
        self.retry = 5

    @property
    def headers(self):
        return {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

    def run(self):
        content = self.fetch_web()

        if content:

            pattern = re.compile('\{bank:\'工商银行\',currency:\'美元\',code:\'USD\',currencyUnit:\'\',cenPrice:\'\',(buyPrice1:\'[.0-9]+\',sellPrice1:\'[.0-9]+\'),.*?\'\}')
            ret_str =  pattern.search(content).group(1)

            buy=re.search('buyPrice1:\'([0-9.]+)\'',ret_str).group(1)
            sell=re.search('sellPrice1:\'([0-9.]+)\'',ret_str).group(1)
            return (buy,sell)

    def start(self):
        buy,sell=self.run()
        sub = '{}: 美元汇率{}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),buy)
        self.logger.info(sub)
        conn=DBSelector().get_mysql_conn('db_stock','qq')
        cmd = 'insert into `usd_ratio` (`price`,`date`) VALUES ({},{!r})'.format(buy,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        self.execute(cmd,(),conn)

        send_message_via_wechat(sub)


    def fetch_web(self):

        for i in range(self.retry):
            try:
                r = requests.get(url=self.url,headers=self.headers)
                if r.status_code==200:
                    r.encoding='gbk'
                    return r.text
                else:
                    continue

            except Exception as e:
                self.logger.error(e)

        return None

def main():
    obj = ForeighExchange()
    obj.start()

if __name__ == '__main__':
    main()
