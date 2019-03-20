# -*- coding: utf-8 -*-
# website: http://30daydo.com
# @Time : 2019/3/19 23:21
# @File : auto_trader.py
import datetime
import logging

import easytrader
import pandas as pd

from setting import get_engine

class AutoTrader():

    def __init__(self):
        self.today = datetime.date.today().strftime('%Y-%m-%d')
        self.engine = get_engine('db_stock',True)

        self.stock_candidates=self.get_candidates()
        self.logger = self.llogger(self.today)
        self.logger.info('程序启动')

        self.user = easytrader.use('ths')
        self.user.connect(r'C:\Tool\gjzq\国金证券同花顺独立下单\xiadan.exe')
        self.position =self.get_position()

    # 获取候选股票池数据
    def get_candidates(self):
        stock_candidate_df = pd.read_sql('tb_stock_candidates',con=self.engine)

    def get_market_data(self):
        market_data_df = pd.read_sql('tb_bond_jisilu',con=self.engine)
        return market_data_df


    # 开盘前统一下单
    def morning_start(self):
        # print(self.user.balance)
        for code in self.stock_candidates:
            # 价格设定为昨天收盘价的-2%

            self.user.buy(code,price=,amount=10)
        print('start')



    def get_position(self):
        return self.user.position()

    def llogger(self,filename):
        logger = logging.getLogger(filename)  # 不加名称设置root logger
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s: - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        # 使用FileHandler输出到文件
        fh = logging.FileHandler(filename + '.log')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        # 使用StreamHandler输出到屏幕
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        # 添加两个Handler
        logger.addHandler(ch)
        logger.addHandler(fh)
        return logger
if __name__=='__main__':
    trader = AutoTrader()
    trader.morning_start()
    print('end')