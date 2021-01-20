# -*- coding: UTF-8 -*-
"""
@author:xda
@file:fund_tencent.py
@time:2021/01/20
"""
from fund_info_spider import FundSpider
import datetime

if __name__ == '__main__':
    now = datetime.datetime.now()
    TODAY = now.strftime('%Y-%m-%d')
    _time = now.strftime('%H:%M:%S')

    if _time < '11:30:00':
        TODAY += 'morning'
    elif _time < '14:45:00':
        TODAY += 'noon'
    else:
        TODAY += 'close'
        # TODAY += 'noon'

    app = FundSpider()
    app.crawl()
    app.update_netvalue(TODAY)
    app.notice_me(TODAY)
