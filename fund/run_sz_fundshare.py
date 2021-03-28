# -*- coding: UTF-8 -*-
"""
@author:xda
@file:run_sz_fundshare.py
@time:2021/01/24
"""

from fund_share_crawl import SZFundShare

if __name__ == '__main__':
    app = SZFundShare(first_use=False)
    app.run()
