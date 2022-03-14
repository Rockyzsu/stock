# -*- coding: utf-8 -*-
# website: http://30daydo.com
# @Time : 2020/8/3 19:01
# @File : closed_end_fund.py

# 抓取封闭式基金数据

import datetime
import requests
import sys

sys.path.append('..')
from configure.settings import DBSelector
from common.BaseService import BaseService
# from configure.util import notify
RETRY = 0


class CloseEndFundCls(BaseService):

    def __init__(self):

        super(CloseEndFundCls, self).__init__('../log/closd_fund.log')
        self.url = 'https://www.jisilu.cn/data/cf/cf_list/'

        self.client = DBSelector().mongo(location_type='qq',async_type=False)

        self.doc = self.client['closed_end_fund'][self.today]

    @property
    def headers(self):
        return {
            'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'}

    def crawl(self):

        global RETRY
        while RETRY < 5:
            try:
                r = requests.get(url=self.url,
                                 headers=self.headers)

            except Exception as e:
                self.logger.error(e)
                RETRY += 1
                continue
            else:
                if r.status_code == 200:
                    js_data = r.json()
                    return js_data

            RETRY += 1
        return None

    def save_mongo(self, row_list):
        try:
            self.doc.insert_many(row_list)
        except Exception as e:
            self.logger.error(e)
            return False
        else:
            return True

    def run(self):
        content = self.crawl()

        if content is None:
            self.logger.error('爬取内容为空')
            return
        rows = content.get('rows')
        row_list = list(map(lambda x: x.get('cell'), rows))

        if not self.save_mongo(row_list):
            self.logger.info('保存失败')
            self.notify(title=f'{self.__class__}jsl封基入库出错')


def main():
    spider = CloseEndFundCls()
    spider.run()


if __name__ == '__main__':
    main()
