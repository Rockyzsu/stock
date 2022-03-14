# -*- coding: UTF-8 -*-
"""
@author:xda
@file:jsl_fund.py
@time:2021/01/20
"""
from fund_jsl import JSLFund

if __name__ == '__main__':
    jsl_spider = JSLFund()
    jsl_spider.crawl()
