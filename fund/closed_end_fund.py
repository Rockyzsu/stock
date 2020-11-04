# -*- coding: utf-8 -*-
# website: http://30daydo.com
# @Time : 2020/8/3 19:01
# @File : closed_end_fund.py

# 抓取封闭式基金数据
import datetime
import requests
from settings import llogger,DBSelector,_json_data
import pymongo

logger = llogger('log/fund.log')
RETRY =0
db = DBSelector()

class CloseEndFundCls():

    def __init__(self):


        self.url ='https://www.jisilu.cn/data/cf/cf_list/'
        self.headers = {
            'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'}
        host=_json_data['mongo']['qq']['host']
        port=_json_data['mongo']['qq']['port']
        user=_json_data['mongo']['qq']['user']
        password=_json_data['mongo']['qq']['password']

        connect_uri = f'mongodb://{user}:{password}@{host}:{port}'
        self.db = pymongo.MongoClient(connect_uri)
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        self.doc = self.db['closed_end_fund'][today]

    def crawl(self):
        global RETRY
        while RETRY < 5:
            try:
                r = requests.get(url=self.url,
                     headers=self.headers)

            except Exception as e:
                logger.error(e)
                RETRY+=1
                continue
            else:
                if r.status_code==200:
                    js_data = r.json()
                    return js_data

            RETRY += 1
        return None


    def save(self,js_data):
        rows = js_data.get('rows')
        row_list =[]
        for row in rows:
            cell = row.get('cell')
            row_list.append(cell)
        try:
            self.doc.insert_many(row_list)
        except Exception as e:
            logger.error(e)
            return False
        else:
            return True

    def run(self):
        content = self.crawl()

        if content is None:
            logger.error('爬取内容为空')
            return

        if self.save(content):
            logger.info('保存成功')
        else:
            logger.info('保存失败')

