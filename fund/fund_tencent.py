# -*- coding: UTF-8 -*-
"""
@author:xda
@file:fund_tencent.py
@time:2021/01/20
"""
from fund_info_spider import TencentFundSpider

if __name__ == '__main__':

    app = TencentFundSpider()
    app.crawl_fund_info_by_code_table()
    app.update_netvalue()
