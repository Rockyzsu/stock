# -*-coding=utf-8-*-
# 估价达到自己的设定值,发邮件通知, 每天2.45发邮件
import tushare as ts
from setting import sendmail, get_engine, trading_time, llogger, is_holiday
import datetime
import time
import pandas as pd
from setting import WechatSend

logger = llogger(__file__)

# 5秒循环检测一次
LOOP__TIME = 60
EXECEPTION_TIME = 2 * LOOP__TIME
MARKET_OPENING = 0

wechat = WechatSend('wei')

# 可转债市场的监控
class ReachTarget():

    def __init__(self):
        self.cb_code, self.name, self.yjl = self.bond()
        self.stocks = dict(zip(self.cb_code, self.name))
        self.stocks_yjl = dict(zip(self.cb_code, self.yjl))
        self.api = ts.get_apis()
        # python3 这个返回的不是list,需要手工转换
        self.code_list = list(self.stocks.keys())


    def bond(self):
        engine = get_engine('db_stock')
        bond_table = 'tb_bond_jisilu'

        try:
            jsl_df = pd.read_sql(bond_table, engine, index_col='index')
            return list(jsl_df[u'正股代码'].values), list(jsl_df[u'正股名称'].values), list(jsl_df[u'溢价率'].values)

        except Exception as e:
            logger.info(e)
            return None

    # 可转债的监测
    def monitor(self):

        while 1:
            current = trading_time()
            if current == MARKET_OPENING:
                try:
                    price_df = ts.quotes(self.code_list, conn=self.api)
                except Exception as  e:
                    logger.info(e)
                    self.api = ts.get_apis()
                    time.sleep(EXECEPTION_TIME)

                else:
                    price_df = price_df[price_df['cur_vol'] != 0]
                    price_df['percent'] = (price_df['price'] - price_df['last_close']) / price_df['last_close'] * 100
                    price_df['percent'] = price_df['percent'].map(lambda x: round(x, 2))
                    ret_dt = price_df[(price_df['percent'] > 2) | (price_df['percent'] < -2)][
                        ['code', 'price', 'percent']]

                    if len(ret_dt) > 0:
                        name_list = []
                        yjl_list = []

                        # 只会提醒一次，下次就不会再出来了
                        for i in ret_dt['code']:
                            name_list.append(self.stocks[i])
                            yjl_list.append(self.stocks_yjl[i])
                            self.code_list.remove(i)

                        ret_dt['name'] = name_list
                        ret_dt[u'溢价率'] = yjl_list
                        ret_dt = ret_dt.sort_values(by='percent', ascending=False)
                        ret_dt = ret_dt.reset_index(drop=True)

                        try:
                            wechat.send_content(ret_dt.to_string())
                            # sendmail(ret_dt.to_string(), '波动的可转债')
                            # logger.info("Send mail successfully at {}".format(datetime.datetime.now()))

                        except Exception as e:
                            logger.info('sending wechat failed')
                            logger.info(e)

                    time.sleep(LOOP__TIME)


            elif current == -1:
                time.sleep(LOOP__TIME)

            elif current == 1:
                try:
                    ts.close_apis(self.api)

                except Exception as e:
                    logger.info('fail to  stop monitor {}'.format(datetime.datetime.now()))
                    logger.info(e)
                exit(0)


if __name__ == '__main__':

    if is_holiday():
        logger.info('Holiday')
        exit(0)

    obj = ReachTarget()
    obj.monitor()
