# -*- coding: utf-8 -*-
# website: http://30daydo.com
# @Time : 2020/2/20 17:06
# @File : etf_info.py
# 获取港股打新数据
import json
import sys
sys.path.append('..')
import datetime
from common.BaseService import BaseService
from configure.settings import DBSelector
from common.aes import AESDecrypt


TIMEOUT = 30  # 超时

class HKNewStock(BaseService):

    def __init__(self):
        super(HKNewStock, self).__init__(logfile='../log/HKNewStock.log')
        self.base_url = 'https://api2.lianghuaipo.com/hk_ipo/get_paged_listed_stock_list'
        self.key = 'eFgabcda1bcda12bc2bcdePgefgadefg'
        self.aes_decoder = AESDecrypt()
        self.aes_decoder.set_key(self.key)
        self.engine = self.get_engine()

    def get_engine(self):
        return DBSelector().mongo('qq')

    @property
    def doc(self):
        return self.engine['db_stock']['hk_new_stock']

    @property
    def headers(self):
        _headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7",
            "cache-control": "no-cache",
            "content-length": "771",
            "content-type": "application/x-www-form-urlencoded",
            "cookie": "Hm_lvt_a93cbc5800037e73153633ace5e288ec=1613452692,1613452700,1613452722,1613454109; Hm_lpvt_a93cbc5800037e73153633ace5e288ec=1613468195; io=BS-6Yzyi4tZknvyjAAEs",
            "origin": "https://www.lianghuaipo.com",
            "pragma": "no-cache",
            "referer": "https://www.lianghuaipo.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36"}
        return _headers

    def form_data(self, page):
        data = {
            "now_page": page,
            "page_cnt": 30,
        }

        return data

    def crawl(self):
        for i in range(1, 31):
            content = self.post(
                url=self.base_url,
                post_data=self.form_data(i),
                _json=True,
            )
            js_data = self.parse(content)

            if js_data:
                self.insert_mongo(js_data)

    def parse(self, content):
        if content.get('msg') != '返回成功':
            return None

        data = content.get('data')
        js_data= self.aes_decoder.decrypt(data)
        if js_data:
            return js_data[:js_data.rfind('}')+1]
        else:
            return None



    def insert_mongo(self, data):

        try:
            data=json.loads(data)
        except Exception as e:
            self.logger.error(e)
            return

        result_list = data.get('result_list')
        for item in result_list:
            item['crawltime']=datetime.datetime.now()

        if len(result_list)==0:
            return

        try:
            self.doc.insert_many(result_list)
        except Exception as e:
            self.logger.error(e)
        else:
            self.logger.info('写入成功')

    def rename(self):
        rename_dict ={
            'issuance_price':'发行定价',
            'market_cap':'发行市值',
            'is_cornerstone':'是否有基石',
            'is_greenshoe':'是否有绿鞋',
            'gray_pct_change':'暗盘涨幅',
            'first_day_pct_change':'首日涨幅',
            'total_pct_change':'累计涨幅',
            'subscription_times':'超额申购倍数',
            'winning_rate':'稳中一手',
            'callback_ratio':'回拨比例',
            'industry_name':'行业',
            'listed_date':'上市日期',
            'sponsors':'保荐机构',
            'apply_people_num':'申购人数',
            'first_hand_winning_rate':'一手中签率',
        }
        self.doc.update_many({},{'$rename':rename_dict})

    def run(self):
        self.logger.info('start to crawl')
        self.crawl()
        self.logger.info('end of crawl')

if __name__ == '__main__':
    app = HKNewStock()
    app.run()
    app.rename()

