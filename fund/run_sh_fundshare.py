# -*- coding: UTF-8 -*-
"""
@author:xda
@file:run_sh_fundshare.py
@time:2021/01/24
"""
from fund_share_crawl import SHFundShare
import fire

def main(kind,date='now'):
    '''
    LOF 20210101
    ETF 2021-01-01
    :param kind:
    :param date:
    :return:
    '''
    # date='2021-03-17'
    # print('data ', date)
    app = SHFundShare(first_use=False,kind=kind,date=date)
    app.run()


if __name__ == '__main__':
    '''
    --kind=ETF --date=now #
    '''
    fire.Fire(main)