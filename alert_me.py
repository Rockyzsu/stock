# -*-coding=utf-8-*-
# 估价达到自己的设定值,发邮件通知, 每天2.45发邮件
import tushare as ts
from setting import get_engine, trading_time, llogger, is_holiday
import datetime
import time
import pandas as pd
import numpy as np

logger = llogger(__file__)

# 循环检测时间
LOOP_TIME = 60
EXECEPTION_TIME = 1
MARKET_OPENING = 0
ALERT_PERCENTAGE = 2

ALERT_PERCENT = 5
ALERT_PERCENT_POOL = 2
file = 'D:\OneDrive\Stock\gj_hold.xls'


# 可转债市场的监控 和 自选池

class ReachTarget():

    def __init__(self):
        self.engine = get_engine('db_stock')

        self.kzz_code, self.kzz_name, self.zg_code, self.name, self.yjl = self.zg_bond()

        self.kzz_stocks = dict(zip(self.kzz_code, self.kzz_name))
        self.zg_stocks = dict(zip(self.zg_code, self.name))

        self.kzz_stocks_yjl = dict(zip(self.kzz_code, self.yjl))
        self.zg_stocks_yjl = dict(zip(self.zg_code, self.yjl))

        self.api = ts.get_apis()

        # python3 这个返回的不是list,需要手工转换

        # self.kzz_code_list = list(self.stocks.keys())
        # pool_code,pool_name=self.stock_pool()
        # self.pool_dict = dict(zip(pool_code,pool_name))
        # self.pool_list= list(self.pool_dict.keys())

        # 添加一部分持仓数据 或者 监测仓

        # self.df = pd.read_table(file, encoding='gbk', dtype={'证券代码': np.str})
        # try:
        #     del self.df['Unnamed: 15']
        # except Exception as e:
        #     logger.error(e)
        #     logger.error('删除多余列失败')
        #
        # code_list = list(self.df['证券代码'].values)
        #
        # # 移除非法证券代码 中签
        # t = [code_list.remove(i) for i in code_list.copy() if i.startswith('7') or i[:2] == '07']
        #
        # self.code_lists=code_list

    # 数据库获取模拟股，这个要废弃
    def stock_pool(self):
        pool_table = 'tb_current_hold'
        pool_df = pd.read_sql(pool_table, self.engine, index_col='index')

        return list(pool_df[u'代码'].values), list(pool_df[u'名字'].values)

    # 获取市场所有可转债数据个股代码 正股
    def zg_bond(self):
        bond_table = 'tb_bond_jisilu'

        try:
            jsl_df = pd.read_sql(bond_table, self.engine)

        except Exception as e:
            logger.info(e)
            return [], [], []

        else:
            return list(jsl_df['可转债代码']), list(jsl_df['可转债名称']), list(jsl_df['正股代码'].values), \
                   list(
                       jsl_df['正股名称'].values), list(
                jsl_df['溢价率'].values)

    # 可转债的监测
    def monitor(self):
        self.has_sent_kzz = dict(zip(self.kzz_code, [datetime.datetime.now()] * len(self.kzz_code)))
        self.has_sent_diff = dict(zip(self.kzz_code, [datetime.datetime.now()] * len(self.kzz_code)))
        self.has_sent_zg = dict(zip(self.zg_code, [datetime.datetime.now()] * len(self.zg_code)))

        while 1:

            current = trading_time()

            if current == MARKET_OPENING:

                self.get_realtime_info(self.kzz_code, self.has_sent_kzz, '转债', self.kzz_stocks, self.kzz_stocks_yjl)
                self.get_realtime_info(self.zg_code, self.has_sent_zg, '正股', self.zg_stocks, self.zg_stocks_yjl)
                self.get_price_diff(self.kzz_code, self.has_sent_diff, '差价')
                time.sleep(LOOP_TIME)

            elif current == -1:
                time.sleep(LOOP_TIME)

            elif current == 1:
                try:
                    ts.close_apis(self.api)

                except Exception as e:
                    logger.info('fail to  stop monitor {}'.format(datetime.datetime.now()))
                    logger.info(e)
                exit(0)

    # 获取实时报价
    def get_realtime_info(self, codes, has_sent, types, stock, yjl):

        try:
            price_df = ts.quotes(codes, conn=self.api)

        except Exception as  e:
            logger.error('获取可转债异常 >>>> {}'.format(e))
            try:
                self.api = ts.get_apis()
            except Exception as e:
                logger.error('异常中存在异常{}'.format(e))

            time.sleep(EXECEPTION_TIME)

        else:

            if len(price_df) != 0:
                price_df = price_df[price_df['cur_vol'] != 0]
                price_df['percent'] = (price_df['price'] - price_df['last_close']) / price_df[
                    'last_close'] * 100
                price_df['percent'] = price_df['percent'].map(lambda x: round(x, 2))
                ret_dt = \
                    price_df[
                        (price_df['percent'] > ALERT_PERCENT) | (price_df['percent'] < -1 * ALERT_PERCENT)][
                        ['code', 'price', 'percent']]

                if len(ret_dt) > 0:
                    name_list = []
                    yjl_list = []

                    # 提醒一次后，下一次的间隔为5分钟后
                    sent_list = []
                    for i in ret_dt['code']:

                        if has_sent[i] <= datetime.datetime.now():
                            name_list.append(stock[i])
                            yjl_list.append(yjl[i])
                            has_sent[i] = has_sent[i] + datetime.timedelta(minutes=5)
                            sent_list.append(ret_dt[ret_dt['code'] == i])

                    if sent_list:
                        send_df = pd.concat(sent_list)
                        send_df['名称'] = name_list
                        send_df['溢价率'] = yjl_list
                        send_df = send_df.sort_values(by='percent', ascending=False)
                        ret_dt1 = send_df.set_index('code', drop=True)
                        content0 = datetime.datetime.now().strftime(
                            '%Y-%m-%d %H:%M:%S') + '\n' + '{}\n'.format(types) + ret_dt1.to_string()

                        try:
                            wechat.send_content(content0)

                        except Exception as e:
                            logger.info('发送微信失败')
                            logger.info(e)

    # 获取差价 可转债
    def get_price_diff(self, codes,has_sent_, types):
        # 针对可转债
        batch = 25
        total = len(codes)
        step = int(total / batch)
        for i in range(0, step + 1):
            code = codes[i * batch:(i + 1) * batch]
            df = ts.get_realtime_quotes(code)  # 一次不超过30个
            df['b1_p'] = df['b1_p'].astype(float)
            df['a1_p'] = df['a1_p'].astype(float)
            result = df[np.abs(df['b1_p'] - df['a1_p']) > 0.5]
            if result.empty:
                continue
            else:
                sent_list = []
                for i in result['code']:

                    if has_sent_[i] <= datetime.datetime.now():
                        has_sent_[i] = has_sent_[i] + datetime.timedelta(minutes=5)
                        sent_list.append(result[result['code'] == i])

                if sent_list:
                    send_df = pd.concat(sent_list)
                    ret_dt1 = send_df.set_index('code', drop=True)
                    ret_dt1 = ret_dt1[['name', 'price', 'bid', 'ask', 'b1_v', 'a1_v']]
                    content0 = datetime.datetime.now().strftime(
                        '%Y-%m-%d %H:%M:%S') + '\n' + '{}\n'.format(types) + ret_dt1.to_string()

                    try:
                        wechat.send_content(content0)
                    except Exception as e:
                        logger.info('发送微信失败')
                        logger.info(e)


if __name__ == '__main__':

    if is_holiday():
        logger.info('Holiday')
        exit(0)

    # 周末的时候不登录微信

    from setting import WechatSend

    wechat = WechatSend('wei')

    obj = ReachTarget()
    obj.monitor()
