# -*-coding=utf-8-*-
# @Time : 2018/8/7 13:45
# @File : foreignexchange.py
# 实时获取外汇
import os
import re
import datetime
import requests
from settings import DBSelector,llogger
logger = llogger('log/usd.log')

class ForeighExchange(object):

    def __init__(self):
        self.url = 'http://data.bank.hexun.com/other/cms/foreignexchangejson.ashx?callback=ShowDatalist'
        self.update_req = 10
        self.retry = 5
        self.headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}

    def run(self):
        content = self.fetch_web()

        if content:
            pattern = re.compile('\{bank:\'工商银行\',currency:\'美元\',code:\'USD\',currencyUnit:\'\',cenPrice:\'\',(buyPrice1:\'[.0-9]+\',sellPrice1:\'[.0-9]+\'),.*?\'\}')
            ret_str =  pattern.search(content).group(1)

            buy=re.search('buyPrice1:\'([0-9.]+)\'',ret_str).group(1)
            sell=re.search('sellPrice1:\'([0-9.]+)\'',ret_str).group(1)
            return (buy,sell)

    def notice(self):
            buy,sell=self.run()
            sub = '{}: 美元汇率{}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'),buy)
            logger.info(sub)
            # sendmail('',sub)

            conn=DBSelector().get_mysql_conn('db_stock','qq')
            cursor = conn.cursor()
            cmd = 'insert into `usd_ratio` (`price`,`date`) VALUES ({},{!r})'.format(buy,datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

            try:
                cursor.execute(cmd)
                conn.commit()
            except Exception as e:
                logger.error(e)
                conn.rollback()

            conn.close()

    def fetch_web(self):

        for i in range(self.retry):

            try:
                r = requests.get(url=self.url,headers=self.headers)
                if r.status_code==200:
                    return r.text
                else:
                    continue

            except Exception as e:
                logger.error(e)

        return None

logger.info('Start')
obj = ForeighExchange()
obj.notice()