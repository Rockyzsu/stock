# -*- coding: utf-8 -*-
# @Time : 2021/3/19 0:04
# @File : fund_annouce.py
# @Author : Rocky C@www.30daydo.com

# 基金公告数据
# http://fund.szse.cn/api/disc/info/find/tannInfo?random=0.5044519418668192&type=2&pageSize=30&pageNum=3
import datetime
import math
import sys

sys.path.append('..')
from common.BaseService import BaseService


class FundAnnouce(BaseService):

    def __init__(self):
        super(FundAnnouce, self).__init__('../log/fund_annouce.log')
        self.PAGE_SIZE=30
        self.base_url = 'http://fund.szse.cn/api/disc/info/find/tannInfo?type=2&pageSize={}&pageNum={}'

    # def get(self, url, _json=False, binary=False, retry=5):
    @property
    def headers(self):
        _header = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "fund.szse.cn",
            "Pragma": "no-cache",
            "Referer": "http://fund.szse.cn/disclosurelist/index.html",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            "X-Request-Type": "ajax",
            "X-Requested-With": "XMLHttpRequest",
        }
        return _header

    def get_page(self):
        content = self.get(self.base_url.format(self.PAGE_SIZE,1), _json=True)
        announceCount=content['announceCount']
        total_page = math.ceil(announceCount/self.PAGE_SIZE)
        return total_page

    def run(self):
        total_page=self.get_page()
        if total_page<1:
            self.logger.info('empty content')
            return

        for page in range(1,total_page):
            content = self.get(self.base_url.format(self.PAGE_SIZE, 1), _json=True)
            self.parse(content)

    def parse(self, content):
        for item in content.get('data'):
            item['crawltime']=datetime.datetime.now()

def main():
    app = FundAnnouce()
    app.run()


if __name__ == '__main__':
    main()
