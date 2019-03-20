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
        self.engine = get_engine('db_stock', True)

        self.stock_candidates = self.get_candidates()
        self.logger = self.llogger('auto_trader_{}'.format(self.today))
        self.logger.info('程序启动')

        self.user = easytrader.use('ths')
        # self.user.prepare('user.json')
        self.user.connect(r'C:\全能行证券交易终端\xiadan.exe')
        self.position = self.get_position()
        self.blacklist_bond = self.get_blacklist()

        print(self.position)

    # 获取候选股票池数据
    def get_candidates(self):
        stock_candidate_df = pd.read_sql(
            'tb_stock_candidates', con=self.engine)
        return stock_candidate_df

    def get_market_data(self):
        market_data_df = pd.read_sql('tb_bond_jisilu', con=self.engine)
        return market_data_df

    # 永远不买的
    def get_blacklist(self):
        black_list_df = pd.read_sql('tb_bond_blacklist', con=self.engine)
        return black_list_df['code'].values

    # 开盘前统一下单
    def morning_start(self):
        # print(self.user.balance)
        codes = self.stock_candidates['code']
        prices = self.stock_candidates['price']
        code_price_dict = dict(zip(codes, prices))
        for code, price in code_price_dict.items():
            # 价格设定为昨天收盘价的-2%
            if code not in self.blacklist_bond:
                buy_price=round(price*0.98,2)
                self.logger.info('代码{}, 当前价格{},设置-2%后的价格为{}'.format(code,price,buy_price))
                try:
                    self.user.buy(code,price=buy_price,amount=10)
                except Exception as e:
                    self.logger.error('买入{}出错'.format(code))
                    self.logger.error(e)

            # self.user.buy(code,price=,amount=10)
        # print('start')

    def get_position(self):
        print(self.user.position)
        return self.user.position

    def llogger(self, filename):
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


if __name__ == '__main__':
    trader = AutoTrader()
    trader.get_position()
    # trader.morning_start()
    print('end')
