# -*- coding: UTF-8 -*-
"""
@author:xda
@file:run_sh_fundshare.py
@time:2021/01/24
"""
from fund_share_update import SHFundShare
import fire

def main(kind,date='now'):
    '''
    LOF 20210101
    ETF 2021-01-01
    :param kind:
    :param date:
    :return:
    '''
    app = SHFundShare(first_use=False,kind=kind,date=date)
    app.run()

if __name__ == '__main__':
    fire.Fire(main)