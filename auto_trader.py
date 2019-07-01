# -*- coding: utf-8 -*-
# website: http://30daydo.com
# @Time : 2019/3/19 23:21
# @File : auto_trader.py
import datetime
import logging
import time
import pymongo
import easyquotation
import easytrader
import pandas as pd
from config import PROGRAM_PATH,MONGO_PORT,MONGO_HOST
from setting import get_engine


class AutoTrader():

    def __init__(self):
        self.today = datetime.date.today().strftime('%Y-%m-%d')

        # self.stock_candidates = self.get_candidates()
        # self.stock_candidates = self.get_candidates()
        self.logger = self.llogger('auto_trader_{}'.format(self.today))
        self.logger.info('程序启动')
        self.user = easytrader.use('gj_client')
        # self.user = easytrader.use('ths')
        self.user.prepare('user.json')
        # self.user.connect(PROGRAM_PATH)
        # self.blacklist_bond = self.get_blacklist()
        # self.q=easyquotation.use('qq')


    # 获取候选股票池数据
    def get_candidates(self):
        stock_candidate_df = pd.read_sql(
            'tb_stock_candidates', con=self.engine)
        stock_candidate_df=stock_candidate_df.sort_values(by='可转债价格')
        return stock_candidate_df

    def get_market_data(self):
        market_data_df = pd.read_sql('tb_bond_jisilu', con=self.engine)
        return market_data_df

    # 永远不买的
    def get_blacklist(self):
        black_list_df = pd.read_sql('tb_bond_blacklist', con=self.engine)
        return black_list_df['code'].values

    # 开盘前统一下单
    def morning_start(self,p):
        # print(self.user.balance)
        codes = self.stock_candidates['可转债代码']
        prices = self.stock_candidates['可转债价格']
        code_price_dict = dict(zip(codes, prices))
        count=0
        while 1:
            count+=1
            logging.info('Looping {}'.format(count))
            
            for code, price in code_price_dict.copy().items():
                # 价格设定为昨天收盘价的-2%
                if code not in self.blacklist_bond:
                    # buy_price=round(price*0.98,2)
                    deal_detail = self.q.stocks(code)
                    close=deal_detail.get(code,{}).get('close') # 昨日收盘
                    ask=deal_detail.get(code,{}).get('ask1') # 卖一
                    bid=deal_detail.get(code,{}).get('bid1') # 买一价
                    current_percent = (ask-close)/close*100
                    # print(current_percent)
                    if current_percent <= p:
                        self.logger.info('>>>>代码{}, 当前价格{}, 开盘跌幅{}'.format(code,bid,current_percent))

                        try:
                            print('code {} buy price {}'.format(code,ask))
                            self.user.buy(code,price=ask+0.1,amount=10)
                        except Exception as e:
                            self.logger.error('>>>>买入{}出错'.format(code))
                            self.logger.error(e)
                        else:
                            del code_price_dict[code]

            # 空的时候退出
            if not code_price_dict:
                break
            time.sleep(20)

    # 持仓仓位
    def get_position(self):
        return self.user.position

    # 持仓仓位 Dataframe格式
    def get_position_df(self):
        position_list = self.get_position()
        # print(position_list)
        df = pd.DataFrame(position_list)
        return df

    def save_position(self):

        self.engine = get_engine('db_position', True)
        df= self.get_position_df()
        # print(df)
        try:
            df.to_sql('tb_position_{}'.format(self.today),con=self.engine,if_exists='replace')
        except Exception as e:
            self.logger.error(e)



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

    def end(self):
        self.logger.info('程序退出')



if __name__ == '__main__':
    trader = AutoTrader()
    # 开盘挂单
    # kaipan_percent = -2
    # trader.morning_start(kaipan_percent)
    trader.save_position()
    # trader.end()

