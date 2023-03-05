# -*- coding: utf-8 -*-
# @Time : 2021/9/6 8:21
# @File : ninwen.py
# @Author : Rocky C@www.30daydo.com

# 宁稳网
import json
import os
import random
import time
from parsel import Selector
import requests
import warnings
import datetime
import re
import pandas as pd
import validate_key
import pickle
import loguru

warnings.filterwarnings("ignore")
logger = loguru.logger


class NinwenSpider():

    def __init__(self):
        super(NinwenSpider, self).__init__()
        self.session = requests.Session()
        self.today = datetime.datetime.now().strftime('%Y-%m-%d')
        logger.info(f'{self.today} start to crawl....')


    @property
    def headers(self):
        _header = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Host": "www.ninwin.cn",
            "Origin": "http://www.ninwin.cn",
            "Referer": "http://www.ninwin.cn/index.php?m=u&c=login",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }

        return _header

    @property
    def json_headers(self):
        headers = {
            "Host": "www.ninwin.cn",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
            "Origin": "https://www.ninwin.cn",
            "Referer": "https://www.ninwin.cn/index.php?m=u&c=login",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7",
        }
        return headers

    def get_image(self):
        rand = int(time.time())
        url = f'http://www.ninwin.cn/index.php?m=verify&a=get&rand={rand}'
        _headers = {"Referer": "http://www.ninwin.cn/index.php?m=u&c=login",
                    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"}
        r = self.session.get(url=url, headers=_headers)
        with open('code.png', 'wb') as fp:
            fp.write(r.content)
        return r.content

    def convert(self, float_str):
        try:
            return_float = float(float_str)
        except:
            return_float = None
        return return_float

    def login(self, code, csrf):
        url = 'https://www.ninwin.cn/index.php?m=u&c=login&a=dorun'
        data = {
            'username': validate_key.username,
            'password': validate_key.password,
            'code': code,
            'backurl': 'https://www.ninwin.cn/',
            'invite': '',
            'csrf_token': csrf
        }
        r = self.session.post(url=url, headers=self.json_headers,
                              data=data
                              )
        ret_js = r.json()
        if ret_js.get('state') == 'success':
            return ret_js.get('referer')

    def get_csrf_token(self):
        url = 'http://www.ninwin.cn/index.php?m=u&c=login'
        content = self.visit_page(url)
        if re.search('value="(.*?)"', content):
            csrf = re.search('value="(.*?)"', content).group(1)
            return csrf

        return None

    def get_bond_data(self):
        url = 'http://www.ninwin.cn/index.php?m=cb&a=cb_all&show_cb_only=Y&show_listed_only=Y'
        content = self.visit_page(url)
        if '回售起始日' in content:
            logger.info("\n获取数据成功\n")
            return content

        else:
            logger.error('获取数据失败')
            return None

    def visit_page(self, url, _headers=None):
        if _headers is None:
            _headers = self.headers
        resp = self.session.get(url=url, headers=_headers)
        content = resp.text
        return content

    @property
    def columns_name(self):
        columns_name_ = [("转债代码", ".//td[2]/text()"),
                         ("转债名称", ".//td[3]/a/text()"),
                         ("满足", ".//td[3]/a/span/@title"),
                         ("发行日期", ".//td[4]/text()"),
                         ("股票代码", ".//td[5]/text()"),
                         ("股票名称", ".//td[6]/text()"),
                         ("行业", ".//td[7]/text()"),
                         ("子行业", ".//td[8]/text()"),
                         ("转债价格", ".//td[9]/text()"),
                         ("本息", ".//td[9]/@title"),
                         ("涨跌", ".//td[10]/spand/text()"),
                         ("日内套利", ".//td[11]/spand/text()"),
                         ("股价", ".//td[12]/text()"),
                         ("正股涨跌", ".//td[13]/spand/text()"),
                         ("剩余本息", ".//td[14]/text()"),
                         ("转股价格", ".//td[15]/text()"),
                         ("转股溢价率", ".//td[16]/text()"),
                         # ("转股期", ".//td[18]/@title"),
                         ("转股价值", ".//td[17]/text()"),
                         ("距离转股日", ".//td[18]/text()"),
                         ("剩余年限", ".//td[19]/text()"),
                         ("回售年限", ".//td[20]/text()"),
                         ("剩余余额", ".//td[21]/text()"),
                         # ("余额", ".//td[20]/text()"),

                         ("成交额(百万)", ".//td[22]/text()"),
                         ("转债换手率", ".//td[23]/text()"),

                         ("余额/市值", ".//td[24]/@title"),

                         ("余额/股本", ".//td[25]/text()"),
                         ("股票市值(亿)", ".//td[26]/text()"),

                         ("P/B", ".//td[27]/text()"),
                         ("税前收益率", ".//td[28]/text()"),
                         ("税后收益率", ".//td[29]/text()"),
                         ("税前回售收益", ".//td[30]/text()"),
                         ("税后回售收益", ".//td[31]/text()"),

                         ("回售价值", ".//td[32]/text()"),
                         ("纯债价值", ".//td[33]/text()"),
                         ("弹性", ".//td[34]/text()"),
                         ("信用", ".//td[35]/text()"),
                         ("折现率", ".//td[36]/text()"),
                         ("老式双低", ".//td[37]/text()"),
                         ("老式排名", ".//td[38]/text()"),
                         ("新式双低", ".//td[39]/text()"),
                         ("新式排名", ".//td[40]/text()"),
                         ("热门度", ".//td[41]/text()"),
                         ]
        return columns_name_

    def patch_fix(self, name, v, node):
        if name == '转股价格' and v is None:
            return True, node.xpath('.//td[15]/a/text()').extract_first()
        return False, None

    def parse(self, content):
        resp = Selector(text=content)
        columns = resp.xpath('//table[@id="cb_hq"]/tbody/tr')
        bond_result_list = []

        for col in columns:
            d = {}
            for item in self.columns_name:
                v = col.xpath(item[1]).extract_first()
                patch, _v = self.patch_fix(item[0], v, col)
                if patch:
                    v = _v

                if isinstance(v, str):
                    v = v.strip()
                d[item[0]] = v
            bond_result_list.append(d)
        return bond_result_list

    def dump_excel(self, bond_info_list):
        df = pd.DataFrame(bond_info_list)
        df.to_excel(f'../data/{self.today}_宁稳.xlsx', encoding="utf8")

    def image_recognize(self, img):
        files = {'file': img}
        data={'sign':validate_key.sign}

        url=validate_key.url

        r = requests.post(url=url, files=files, data=data,timeout=20)
        try:
            code = r.json().get('code')
            print(r.json())
        except Exception as e:
            logger.error(e)
            raise e
        else:
            return code

    def check_name(self, csrf_token):
        url = 'https://www.ninwin.cn/index.php?m=u&c=login&a=checkname'
        data = {'csrf_token': csrf_token,
                'username': validate_key.username}
        r = self.session.post(url=url, headers=self.json_headers, data=data)

    def check_cookies(self, csrf, code):
        url = f'https://www.ninwin.cn/index.php?m=verify&a=check&csrf_token={csrf}&code={code}'
        time.sleep(0.5)
        content = self.visit_page(url, _headers=self.json_headers)

    def run(self):
        csrf = self.get_csrf_token()
        while 1:
            img = self.get_image()
            code = self.image_recognize(img)
            print(code)
            self.check_name(csrf)
            self.check_cookies(csrf, code)
            time.sleep(0.5)
            ref_url = self.login(code, csrf)
            if ref_url is None:
                logger.info('识别错误或者密码错误，正在重试.....')
                time.sleep(random.randint(1, 5))
                continue

            self.visit_page(ref_url)
            content = self.get_bond_data()
            bond_info_list = self.parse(content)
            self.dump_excel(bond_info_list)
            logger.info('获取结束')
            os.remove('code.png')
            break


if __name__ == '__main__':
    app = NinwenSpider()
    app.run()
