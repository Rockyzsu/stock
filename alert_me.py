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
ALERT_PERCENTAGE =2

ALERT_PERCENT = 5
ALERT_PERCENT_POOL= 2
file = 'D:\OneDrive\Stock\gj_hold.xls'
# 可转债市场的监控 和 自选池
class ReachTarget():

    def __init__(self):
        self.engine = get_engine('db_stock')
        self.cb_code, self.name, self.yjl = self.bond()
        self.stocks = dict(zip(self.cb_code, self.name))
        self.stocks_yjl = dict(zip(self.cb_code, self.yjl))
        self.api = ts.get_apis()

        # python3 这个返回的不是list,需要手工转换


        self.kzz_code_list = list(self.stocks.keys())
        pool_code,pool_name=self.stock_pool()
        self.pool_dict = dict(zip(pool_code,pool_name))
        self.pool_list= list(self.pool_dict.keys())

        # 添加一部分持仓数据 或者 监测仓

        self.df = pd.read_table(file, encoding='gbk', dtype={'证券代码': np.str})
        del self.df['Unnamed: 15']
        code_list = list(self.df['证券代码'].values)

        # 移除非法证券代码 中签
        t = [code_list.remove(i) for i in code_list.copy() if i.startswith('7') or i[:2] == '07']
        self.code_lists=code_list

    def stock_pool(self):
        pool_table = 'tb_current_hold'
        pool_df = pd.read_sql(pool_table, self.engine, index_col='index')

        return list(pool_df[u'代码'].values), list(pool_df[u'名字'].values)

    def bond(self):
        bond_table = 'tb_bond_jisilu'

        try:
            jsl_df = pd.read_sql(bond_table, self.engine)
            return list(jsl_df['正股代码'].values), list(jsl_df['正股名称'].values), list(jsl_df['溢价率'].values)

        except Exception as e:
            logger.info(e)
            return None

    # 可转债的监测
    def monitor(self):

        while 1:

            current = trading_time()
            
            if current == MARKET_OPENING:

                # 持仓

                try:
                    price_df = ts.quotes(self.code_lists, conn=self.api)
                except Exception as e:
                    logger.error('获取持仓数据异常>>> {}'.format(e))

                    try:
                        self.api=ts.get_apis()
                    except Exception as e:
                        logger.error('重新启动get_api出错 {}'.format(e))

                else:
                    # 去除不合法的数据

                    price_df = price_df.dropna()
                    filter_df = price_df[price_df['last_close'] != 0]
                    filter_df = filter_df.reset_index(drop=True)
                    filter_df['percent'] = (filter_df['price'] - filter_df['last_close']) / filter_df[
                        'last_close'] * 100
                    filter_df['percent'] = filter_df['percent'].map(lambda x: round(x, 2))
                    ret_df = filter_df[
                        (filter_df['percent'] > ALERT_PERCENTAGE) | (filter_df['percent'] < ALERT_PERCENTAGE * -1)]
                    if len(ret_df)>0:
                        d = dict(zip(list(self.df['证券代码'].values), list(self.df['证券名称'])))
                        ret_df['name'] = ret_df['code'].map(lambda x: d.get(x))
                        ret_df['amount'] = ret_df['amount'].map(lambda x: round(x / 10000, 1))
                        rename_column = {'code': '证券代码', 'name': '证券名称', 'price': '当前价格', 'percent': '涨幅',
                                         'amount': '成交金额(万)'}

                        ret_df = ret_df.rename(columns=rename_column)
                        ret = ret_df[list(rename_column.values())]
                        ret = ret.reset_index(drop=True)

                        content = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'\n'+ret.to_string()
                        try:
                            wechat.send_content(content)
                        except Exception as e:
                            logger.error('微信发送失败 {}'.format(e))

                # 可转债
                try:
                    price_df = ts.quotes(self.kzz_code_list, conn=self.api)
                except Exception as  e:
                    logger.error('获取可转债异常 >>>> {}'.format(e))
                    try:
                        self.api = ts.get_apis()
                    except Exception as e:
                        logger.error('异常中存在异常{}'.format(e))
                        # continue

                    time.sleep(EXECEPTION_TIME)
                    # continue

                else:

                    if len(price_df)!=0:
                        # continue

                        price_df = price_df[price_df['cur_vol'] != 0]
                        price_df['percent'] = (price_df['price'] - price_df['last_close']) / price_df['last_close'] * 100
                        price_df['percent'] = price_df['percent'].map(lambda x: round(x, 2))
                        ret_dt =  price_df[(price_df['percent'] > ALERT_PERCENT) | (price_df['percent'] < -1 * ALERT_PERCENT)][
                            ['code', 'price', 'percent']]


                        if len(ret_dt) > 0:
                            name_list = []
                            yjl_list = []

                            # 只会提醒一次，下次就不会再出来了
                            for i in ret_dt['code']:
                                name_list.append(self.stocks[i])
                                yjl_list.append(self.stocks_yjl[i])
                                self.kzz_code_list.remove(i)

                            ret_dt['name'] = name_list
                            ret_dt[u'溢价率'] = yjl_list
                            ret_dt = ret_dt.sort_values(by='percent', ascending=False)
                            ret_dt1 = ret_dt.reset_index(drop=True)

                            content0 = datetime.datetime.now().strftime(
                                '%Y-%m-%d %H:%M:%S') + '\n' + ret_dt1.to_string()
                            try:
                                wechat.send_content(content0)
                            except Exception as e:
                                logger.info('发送微信失败')
                                logger.info(e)


                # 自选池
                try:
                    price_pool = ts.quotes(self.pool_list, conn=self.api)

                except Exception as e:
                    logger.error('获取自选错误 >>> {}'.format(e))
                    try:
                        self.api = ts.get_apis()
                    except Exception as e:
                        logger.error('异常中出现异常 {}'.format(e))
                        time.sleep(EXECEPTION_TIME)
                        # continue

                    # continue
                else:

                    if len(price_pool)==0:
                        continue

                    price_pool = price_pool[price_pool['cur_vol'] != 0]
                    price_pool['percent'] = (price_pool['price'] - price_pool['last_close']) / price_pool['last_close'] * 100
                    price_pool['percent'] = price_pool['percent'].map(lambda x: round(x, 2))
                    ret_dt_pool =  price_pool[(price_pool['percent'] > ALERT_PERCENT_POOL) | (price_pool['percent'] < -1 * ALERT_PERCENT_POOL)][
                        ['code', 'price', 'percent']]

                    if len(ret_dt_pool) > 0:
                        name_list_pool = []

                        # 只会提醒一次，下次就不会再出来了
                        for i in ret_dt_pool['code']:
                            name_list_pool.append(self.pool_dict[i])
                            self.pool_list.remove(i)

                        ret_dt_pool['name'] = name_list_pool
                        ret_dt_pool = ret_dt_pool.sort_values(by='percent', ascending=False)
                        ret_dt_pool = ret_dt_pool.reset_index(drop=True)
                        content1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'\n'+ret_dt_pool.to_string()
                        try:
                            wechat.send_content(content1)

                        except Exception as e:
                            logger.error('微信发送异常{}'.format(e))

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


if __name__ == '__main__':

    if is_holiday():
        logger.info('Holiday')
        exit(0)

    # 周末的时候不登录微信

    from setting import WechatSend

    wechat = WechatSend('wei')

    obj = ReachTarget()
    obj.monitor()
