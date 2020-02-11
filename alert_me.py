# -*-coding=utf-8-*-
# 估价达到自己的设定值,发邮件通知, 每天2.45发邮件
import requests
import tushare as ts
from settings import get_engine, trading_time, llogger, is_holiday, get_mysql_conn
import datetime
import time
import pandas as pd
import numpy as np
import os
import tkinter
import tkinter
import tkinter.messagebox #弹窗库
import threading

def show_box(msg):
    tkinter.messagebox.showinfo('注意',msg)


dirname = os.path.dirname(__file__)
full_name = os.path.join(dirname, 'log/alert_me_{}.log'.format(datetime.date.today()))
logger = llogger(full_name)

# 循环检测时间
LOOP_TIME = 60
EXECEPTION_TIME = 20
MARKET_OPENING = 0
# ALERT_PERCENTAGE = 3
DELTA_TIME = 30
ZG_ALERT_PERCENT = 8
ZZ_ALERT_PERCENT = 8
CW_ALERT_PERCENT=-5
DIFF_DELTA_TIME=30
# ALERT_PERCENT_POOL = 3
DIFF_V = 40 # quote 接口以千为单位

file = 'D:\OneDrive\Stock\gj_hold.xls'


# 可转债市场的监控 和 自选池

class ReachTarget():

    def __init__(self):
        self.engine = get_engine('db_stock')
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

    def all_bond_market(self):
        self.kzz_code, self.kzz_name, self.zg_code, self.name, self.yjl = self.zg_bond()

        self.kzz_stocks = dict(zip(self.kzz_code, self.kzz_name))
        self.zg_stocks = dict(zip(self.zg_code, self.name))

        self.kzz_stocks_yjl = dict(zip(self.kzz_code, self.yjl))
        self.zg_stocks_yjl = dict(zip(self.zg_code, self.yjl))

        return (
                self.kzz_stocks,
                self.zg_stocks,
                self.kzz_stocks_yjl,
                self.zg_stocks_yjl)

    # 数据库获取模拟股，这个要废弃
    def stock_pool(self):
        pool_table = 'tb_current_hold'
        pool_df = pd.read_sql(pool_table, self.engine, index_col='index')

        return list(pool_df['代码'].values), list(pool_df['名字'].values)

    # 判断市场
    def identify_market(self,x):
        if x.startswith('3') or x.startswith('6') or x.startswith('0'):
            return False
        else:
            return True

    # 获取当前持仓个股
    def get_current_position(self):
        engine = get_engine('db_position')

        df = pd.read_sql('tb_position_2019-06-17', con=engine)

        # 只关注可转债
        df=df[df['证券代码'].map(self.identify_market)]

        kzz_stocks = dict(zip(list(df['证券代码'].values), list(df['证券名称'].values)))

        cons = get_mysql_conn('db_stock', 'local')
        cursor = cons.cursor()
        query_cmd = 'select 正股代码,正股名称,溢价率 from tb_bond_jisilu where 可转债代码=%s'
        zg_stocks = {}
        kzz_yjl = {}
        zg_yjl = {}
        for code in kzz_stocks:
            cursor.execute(query_cmd, (code))
            ret = cursor.fetchone()
            if ret:
                zg_stocks[ret[0]] = ret[1]
                kzz_yjl[code] = ret[2]
                zg_yjl[ret[0]] = ret[2]

        # 可转债代码
        # dict,dict,dict,dict
        return (kzz_stocks, zg_stocks, kzz_yjl, zg_yjl)

    # 获取市场所有可转债数据个股代码 正股
    def zg_bond(self):
        bond_table = 'tb_bond_jisilu'

        try:
            jsl_df = pd.read_sql(bond_table, self.engine)

        except Exception as e:
            logger.info(e)
            return [], [], [], [], []

        else:
            return list(jsl_df['可转债代码']), list(jsl_df['可转债名称']), list(jsl_df['正股代码'].values), \
                   list(jsl_df['正股名称'].values), list(jsl_df['溢价率'].values)

    # 可转债的监测
    def monitor(self,total_market=True):
        '''
        total_market 默认监控全市场 total_market = True
        '''
        if total_market:
            (kzz_stocks, zg_stocks, kzz_yjl, zg_yjl) = self.all_bond_market()
        else:
            (kzz_stocks, zg_stocks, kzz_yjl, zg_yjl) = self.get_current_position()

        zg_code = list(zg_stocks.keys())
        kzz_code = list(kzz_stocks.keys())
        self.has_sent_kzz = dict(zip(kzz_code, [datetime.datetime.now()] * len(kzz_code)))
        self.has_sent_diff = dict(zip(kzz_code, [datetime.datetime.now()] * len(kzz_code)))
        self.has_sent_zg = dict(zip(zg_code, [datetime.datetime.now()] * len(zg_code)))

        while 1:

            current = trading_time()
            if current == MARKET_OPENING:

                self.get_realtime_info(kzz_code, self.has_sent_kzz, '转债', kzz_stocks, kzz_yjl,
                                       ZZ_ALERT_PERCENT)
                self.get_realtime_info(zg_code, self.has_sent_zg, '正股', zg_stocks, zg_yjl,
                                       ZG_ALERT_PERCENT)
                self.get_price_diff(codes=kzz_code, has_sent_=self.has_sent_diff, types='差价',kzz_stocks=kzz_stocks,kzz_stocks_yjl=kzz_yjl)


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
    def get_realtime_info(self, codes, has_sent, types, stock, yjl, percent):

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
                        (price_df['percent'] > percent) | (price_df['percent'] < -1 * percent)][
                        ['code', 'price', 'percent']]

                if len(ret_dt) > 0:

                    # 提醒一次后，下一次的间隔为DELTA_TIME分钟后
                    # sent_list = []
                    for i in ret_dt['code']:

                        if has_sent[i] <= datetime.datetime.now():
                            name_list = []
                            yjl_list = []
                            name_list.append(stock[i])
                            yjl_list.append(yjl[i])
                            has_sent[i] = datetime.datetime.now() + datetime.timedelta(minutes=DELTA_TIME)

                            ret_dt1 = ret_dt[ret_dt['code'] == i]
                            ret_dt1['名称'] = name_list
                            ret_dt1['溢价率'] = yjl_list

                            name = ret_dt1['名称'].values[0]
                            price = ret_dt1['price'].values[0]
                            percent = ret_dt1['percent'].values[0]
                            yjl_v = ret_dt1['溢价率'].values[0]
                            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                            content0 = '{t}\n{name}:价格:{price} 涨幅:{percent},溢价率:{yjl}'.format(name=name, price=price,
                                                                                              percent=percent,
                                                                                              yjl=yjl_v, t=now)

                            logger.info(content0)

                            try:
                                wechat.send_content(content0)

                            except Exception as e:
                                logger.info('发送微信失败')
                                logger.info(e)

    # 获取差价 可转债
    def get_price_diff(self, codes, has_sent_, types,kzz_stocks,kzz_stocks_yjl):
        # 针对可转债
        try:
            df = ts.quotes(codes, conn=self.api)

        except Exception as  e:
            logger.error('获取可转债异常 >>>> {}'.format(e))
            try:
                self.api = ts.get_apis()
            except Exception as e:
                logger.error('异常中存在异常{}'.format(e))

            time.sleep(EXECEPTION_TIME)

        else:
            df['bid1'] = df['bid1'].astype(float)
            df['ask1'] = df['ask1'].astype(float)
            df['diff'] = np.abs(df['bid1'] - df['ask1'])
            result = df[df['diff'] >= DIFF_V]
            if result.empty:
                # continue
                return
            else:
                for j in result['code']:

                    if has_sent_[j] <= datetime.datetime.now():
                        has_sent_[j] = datetime.datetime.now() + datetime.timedelta(minutes=DIFF_DELTA_TIME)
                        name_list = []
                        yjl_list = []
                        name_list.append(kzz_stocks[j])
                        yjl_list.append(kzz_stocks_yjl[j])
                        ret_dt1 = result[result['code'] == j]
                        ret_dt1['名称'] = name_list
                        ret_dt1['溢价率'] = yjl_list
                        # ret_dt1 = ret_dt1.set_index('code', drop=True)

                        code = j
                        name = ret_dt1['名称'].values[0]
                        price = ret_dt1['price'].values[0]
                        bid = ret_dt1['bid1'].values[0]
                        ask = ret_dt1['ask1'].values[0]
                        diff = round(ret_dt1['diff'].values[0], 2)
                        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        content0 = '{t}\n{code}::{name}:价格:{price} 买1:{bid} 卖1:{ask}差价:{diff}'.format(code=code,
                                                                                                      name=name,
                                                                                                      price=price,
                                                                                                      bid=bid, ask=ask,
                                                                                                      diff=diff, t=now)
                        logger.info(content0)
                        try:
                            wechat.send_content(content0)
                        except Exception as e:
                            logger.info('发送微信失败')
                            logger.info(e)

# 使用jsl作为数据源
class ReachTargetJSL():
    def __init__(self):
        self.session = requests.Session()
        self.cookies = {
            'auto_reload': 'true',
            'kbzw_r_uname': '%E9%87%8F%E5%8C%96%E8%87%AA%E7%94%B1%E4%B9%8B%E8%B7%AF',
            'kbz_newcookie': '1',
            'kbzw__Session': '1kmak8h8v6pscf5brjllb9hfk3',
            'Hm_lvt_164fe01b1433a19b507595a43bf58262': '1578275141,1578879529',
            'Hm_lpvt_164fe01b1433a19b507595a43bf58262': '1579488732',
        }

        self.headers = {
            'Sec-Fetch-Mode': 'cors',
            'Origin': 'https://www.jisilu.cn',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Cache-Control': 'no-cache',
            'Referer': 'https://www.jisilu.cn/data/cbnew/',
            'Sec-Fetch-Site': 'same-origin',
        }

        self.params = (
            ('___jsl', 'LST___t=1579488785838'),
        )

        self.data = {
            'fprice': '',
            'tprice': '',
            'volume': '',
            'svolume': '',
            'premium_rt': '',
            'ytm_rt': '',
            'rating_cd': '',
            'is_search': 'Y',
            'btype': '',
            'listed': 'Y',
            'sw_cd': '',
            'bond_ids': '',
            'rp': '50'
        }

    def get_info(self):

        try:
            response = self.session.post('https://www.jisilu.cn/data/cbnew/cb_list/', headers=self.headers, params=self.params,
                                    cookies=self.cookies, data=self.data, timeout=30)
        except Exception as e:
            print(e)
            print('网络超时')
        else:
            ret = response.json()

        for body_dict in ret.get('rows', []):
            # print(item)
            item = body_dict.get('cell', {})
            bond_nm = item.get('bond_nm', '').strip()
            full_price = item.get('full_price')
            if full_price:
                full_price = float(full_price)

            remium_rt = item.get('premium_rt')

            increase_rt = item.get('increase_rt')
            if increase_rt:
                increase_rt = increase_rt.replace('%','')
                increase_rt = float(increase_rt)

            if abs(increase_rt)> ZZ_ALERT_PERCENT:
                '''
                发送消息
                t = threading.Thread(target=show_box, args=(bond_nm,))
                t.start()
                '''

                


if __name__ == '__main__':

    if is_holiday():
        logger.info('Holiday')
        exit(0)

    # 周末的时候不登录微信

    from settings import WechatSend
    #
    wechat = WechatSend('wei')
    logger.info('{} 开始实时行情爬取'.format(datetime.date.today()))
    jsl = True
    if jsl:
        obj = ReachTargetJSL()
        obj.get_info()

    else:
        obj = ReachTarget()
        obj.monitor()
