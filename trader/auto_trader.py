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
from config import PROGRAM_PATH, MONGO_PORT, MONGO_HOST
from configure.settings import DBSelector

SELL = 7  # 配置为8%个点卖

DB = DBSelector()


class AutoTrader():

    def __init__(self):
        self.today = datetime.date.today().strftime('%Y-%m-%d')

        # self.stock_candidates = self.get_candidates()
        # self.stock_candidates = self.get_candidates()
        self.logger = self.llogger('log/auto_trader_{}'.format(self.today))
        self.logger.info('程序启动')
        self.user = easytrader.use('gj_client')
        # self.user = easytrader.use('ths')
        self.user.prepare('user.json')
        # self.user.connect(PROGRAM_PATH)
        # self.blacklist_bond = self.get_blacklist()
        # self.q=easyquotation.use('qq')

        self.yesterday = datetime.datetime.now() + datetime.timedelta(days=-1)
        # 如果是周一 加一个判断
        self.yesterday = self.yesterday.strftime('%Y-%m-%d')

    def get_close_price(self):

        conn = DB.get_mysql_conn('db_jisilu', 'qq')
        cursor = conn.cursor()

        cmd = 'select 可转债代码,可转债价格 from `tb_jsl_{}`'.format(self.yesterday)
        try:
            cursor.execute(cmd)
            result = cursor.fetchall()
        except Exception as e:
            return None

        else:
            d = {}
            for item in result:
                d[item[0]] = item[1]
            return d

    # 设置涨停 附近卖出 挂单
    def set_ceiling(self):
        position = self.get_position()
        # print(position)
        code_price = self.get_close_price()

        for each_stock in position:
            try:
                code = each_stock.get('证券代码')
                amount = int(each_stock.get('可用余额', 0))
                if amount <= 0.1:
                    continue
                close_price = code_price.get(code, None)
                buy_price = round(close_price * (1 + SELL * 0.01), 1)
                self.user.sell(code, price=buy_price, amount=amount)

            except Exception as e:

                self.logger.error(e)

    # 获取候选股票池数据
    def get_candidates(self):
        stock_candidate_df = pd.read_sql(
            'tb_stock_candidates', con=self.engine)
        stock_candidate_df = stock_candidate_df.sort_values(by='可转债价格')
        return stock_candidate_df

    def get_market_data(self):
        market_data_df = pd.read_sql('tb_bond_jisilu', con=self.engine)
        return market_data_df

    # 永远不买的
    def get_blacklist(self):
        black_list_df = pd.read_sql('tb_bond_blacklist', con=self.engine)
        return black_list_df['code'].values

    # 开盘前统一下单
    def morning_start(self, p):
        # print(self.user.balance)
        codes = self.stock_candidates['可转债代码']
        prices = self.stock_candidates['可转债价格']
        code_price_dict = dict(zip(codes, prices))
        count = 0
        while 1:
            count += 1
            logging.info('Looping {}'.format(count))

            for code, price in code_price_dict.copy().items():
                # 价格设定为昨天收盘价的-2%
                if code not in self.blacklist_bond:
                    # buy_price=round(price*0.98,2)
                    deal_detail = self.q.stocks(code)
                    close = deal_detail.get(code, {}).get('close')  # 昨日收盘
                    ask = deal_detail.get(code, {}).get('ask1')  # 卖一
                    bid = deal_detail.get(code, {}).get('bid1')  # 买一价
                    current_percent = (ask - close) / close * 100
                    # print(current_percent)
                    if current_percent <= p:
                        self.logger.info('>>>>代码{}, 当前价格{}, 开盘跌幅{}'.format(code, bid, current_percent))

                        try:
                            print('code {} buy price {}'.format(code, ask))
                            self.user.buy(code, price=ask + 0.1, amount=10)
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
        '''
        [{'证券代码': '128012', '证券名称': '辉丰转债', '股票余额': 10.0, '可用余额': 10.0,
        '市价': 97.03299999999999, '冻结数量': 0, '参考盈亏': 118.77, '参考成本价': 85.156,
        '参考盈亏比例(%)': 13.947000000000001, '市值': 970.33, '买入成本': 85.156, '市场代码': 1,
        '交易市场': '深圳Ａ股', '股东帐户': '0166448046', '实际数量': 10, 'Unnamed: 15': ''}
        :return:
        '''
        return self.user.position

    # 持仓仓位 Dataframe格式
    def get_position_df(self):
        position_list = self.get_position()
        # print(position_list)
        df = pd.DataFrame(position_list)
        return df

    def save_position(self):

        self.engine = DB.get_engine('db_position', 'qq')
        df = self.get_position_df()
        # print(df)
        try:
            df.to_sql('tb_position_{}'.format(self.today), con=self.engine, if_exists='replace')
        except Exception as e:
            self.logger.error(e)

    def llogger(self, filename):
        logger = logging.getLogger(filename)  # 不加名称设置root logger
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - Line:%(lineno)d:-%(levelname)s: - %(message)s',
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
    # trader.save_position()
    # trader.end()
    trader.set_ceiling()
