# -*- coding: utf-8 -*-
# website: http://30daydo.com
# @Time : 2019/10/24 0:03
# @File : new_stock_fund.py

# 获取打新基金数据
import requests
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import logging
from scrapy.selector import Selector

logger = logging.getLogger()
PATH = r'C:\OneDrive\Python\selenium\chromedriver.exe'

class TianTianFund():
    def __init__(self):

        # 未上市

        self.wss_url='http://fund.eastmoney.com/data/dxgjj_xgccjjyl.html#wss;SUMPLACE;desc;1'
        options = webdriver.ChromeOptions()
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 999999.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')

        self.driver = webdriver.Chrome(executable_path=PATH,
                                  chrome_options=options)

    def get_fund(self):
        self.driver.get(self.wss_url)
        time.sleep(5)
        text=self.driver.page_source
        response = Selector(text=text)
        nodes = response.xpath('//tbody[@id="datalistwss_body"]/tr')

        for node in nodes:
            code = node.xpath('.//td[2]/a/text()').extract_first()
            name = node.xpath('.//td[3]/a/text()').extract_first()
            hit_count = node.xpath('.//td[6]/a[1]/text()').extract_first()
            fund_url = node.xpath('.//td[6]/a[1]/@href').extract_first()
            full_url = 'http://fund.eastmoney.com/data/'+fund_url
            new_stock_amount = node.xpath('.//td[6]/text()').extract_first()
            self.driver.get(fund_url)
            time.sleep(5)
            sub_response = Selector(text=self.driver.page_source)
            sub_nodes = sub_response.xpath('//tbody[@id="datalist_body"]/tr')

            new_stock_list = []
            for sub_node in sub_nodes:
                d={}
                stock_code = sub_node.xpath('.//td[2]/a/text()').extract_first()
                stock_name = sub_node.xpath('.//td[3]/a/text()').extract_first()
                assign_mount = sub_node.xpath('.//td[9]/text()').extract_first()
                d['新股代码']=stock_code
                d['新股名称']=stock_name
                d['中的金额-万元']=assign_mount
                new_stock_list.append(d)

            print(new_stock_list)





    def start(self):
        self.get_fund()

        self.driver.close()


if __name__=='__main__':
    fund = TianTianFund()
    fund.start()