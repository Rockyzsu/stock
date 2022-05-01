# 使用jsl作为数据源
import requests
import sys

sys.path.append('..')
import time
import threading
from configure.settings import config

from common.BaseService import BaseService, HistorySet
from configure.util import get_holding_list
from datahub.jsl_login import login

ACCESS_INTERVAL = config['jsl_monitor']['ACCESS_INTERVAL']
MONITOR_PERCENT = config['jsl_monitor']['MONITOR_PERCENT']
EXPIRE_TIME = config['jsl_monitor']['EXPIRE_TIME']
HOLDING_FILENAME = config['holding_file']
JSL_USER = config['jsl_monitor']['JSL_USER']
JSL_PASSWORD = config['jsl_monitor']['JSL_PASSWORD']

FILTER_REDEEM = True #过滤强赎

class ReachTargetJSL(BaseService):
    def __init__(self):
        super(ReachTargetJSL, self).__init__(f'../log/{self.__class__.__name__}.log')
        self.session = requests.Session()
        self.__headers = {
            'Host': 'www.jisilu.cn', 'Connection': 'keep-alive', 'Pragma': 'no-cache',
            'Cache-Control': 'no-cache', 'Accept': 'application/json,text/javascript,*/*;q=0.01',
            'Origin': 'https://www.jisilu.cn', 'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0(WindowsNT6.1;WOW64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/67.0.3396.99Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'Referer': 'https://www.jisilu.cn/login/',
            'Accept-Encoding': 'gzip,deflate,br',
            'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8',
        }
        ts = int(time.time() * 1000)
        self.params = (
            ('___jsl', f'LST___t={ts}'),
        )
        self.holding_list = get_holding_list(filename=HOLDING_FILENAME)
        self.query_condition = {
            "fprice": None,
            "tprice": None,
            "curr_iss_amt": None,
            "volume": None,
            "svolume": None,
            "premium_rt": None,
            "ytm_rt": None,
            "rating_cd": None,
            "is_search": "N",
            "btype": "C",
            "listed": "Y",
            "qflag": "N",
            "sw_cd": None,
            "bond_ids": None,
            "rp": 50,
        }

        self.history = HistorySet(expire=EXPIRE_TIME)
        self.get_session()

    def get_session(self):
        self.session = login(JSL_USER, JSL_PASSWORD)

    def get(self, *args, **kwargs):
        # 复写
        try:
            response = self.session.post('https://www.jisilu.cn/data/cbnew/cb_list_new/', headers=self.__headers,
                                         params=self.params,
                                         data=self.query_condition, timeout=30)
        except Exception as e:
            self.logger.error(e)
            return None
        else:
            ret = response.json()
            return ret

    def __convert__(self, string):

        string = string.replace('%', '')
        try:
            string = round(float(string), 1)
        except:
            return 0
        else:
            return string

    def monitor(self):

        while True:

            # if True:
            if self.trading_time() == 0:
                ret = self.get()

                if not ret:
                    time.sleep(5)
                    continue

                for body_dict in ret.get('rows', []):
                    item = body_dict.get('cell', {})

                    bond_nm = item.get('bond_nm', '').strip()
                    bond_id = item.get('bond_id', '').strip()

                    full_price = round(item.get('price'),1)
                    # premium_rt = self.__convert__(item.get('premium_rt'))
                    premium_rt = item.get('premium_rt')

                    sincrease_rt = item.get('sincrease_rt')  # 正股涨幅

                    if sincrease_rt is None:
                        # 正股停牌了
                        continue

                    increase_rt = item.get('increase_rt')
                    curr_iss_amt = round(item.get('curr_iss_amt'),2)  # 剩余规模
                    word = '涨停 ' if sincrease_rt > 0 else '跌停'

                    flag = item.get('redeem_icon')
                    if FILTER_REDEEM and (flag=='Y' or flag=='0' or flag=='R'):
                        #过滤强赎
                        continue

                    if curr_iss_amt>15:
                        # 过滤规模大于15亿
                        continue

                    if bond_id in self.holding_list and abs(increase_rt) > 9 and self.history.is_expire(bond_id):
                        text = f'{bond_nm} {increase_rt},价格：{full_price}; 正股{sincrease_rt}; 规模：{curr_iss_amt}; 溢价率：{premium_rt}'
                        t = threading.Thread(target=self.notify, args=(text,))
                        t.start()
                        self.history.add(bond_id)

                    if abs(sincrease_rt) >= MONITOR_PERCENT and self.history.is_expire(bond_id):
                        text = f'{bond_nm} {increase_rt},价格：{full_price}; 正股{sincrease_rt}; 规模：{curr_iss_amt}; 溢价率：{premium_rt}'
                        t = threading.Thread(target=self.notify, args=(text,))
                        t.start()
                        self.logger.info(f'{bond_nm} {word}')
                        self.history.add(bond_id)


            elif self.trading_time() == 1:
                break

            time.sleep(ACCESS_INTERVAL)


if __name__ == "__main__":
    app = ReachTargetJSL()
    app.monitor()
