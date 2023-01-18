# 使用jsl作为数据源
import json

import redis
import requests
import sys

sys.path.append('..')
import time
import threading
from configure.settings import config

from common.BaseService import BaseService, HistorySet
from datahub.jsl_login import login

ACCESS_INTERVAL = config['jsl_monitor']['ACCESS_INTERVAL']

ZZ_PERCENT = config['jsl_monitor']['ZZ_PERCENT']
ZG_PERCENT = config['jsl_monitor']['ZG_PERCENT']
REMAIN_SIZE = config['jsl_monitor']['REMAIN_SIZE']

EXPIRE_TIME = config['jsl_monitor']['EXPIRE_TIME']
HOLDING_FILENAME = config['holding_file']
JSL_USER = config['jsl_monitor']['JSL_USER']
JSL_PASSWORD = config['jsl_monitor']['JSL_PASSWORD']
ACCESS_INTERVAL_REALTIME = config['jsl_monitor']['ACCESS_INTERVAL_REALTIME']
FILTER_REDEEM = True #过滤强赎
REDIS_KEY = config['jsl_monitor']['REDIS_KEY']
REDIS_HOST=config['redis']['uc']['host']
REDIS_PORT=config['redis']['uc']['port']
REDIS_PASSWORD =config['redis']['uc']['password']

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
        self.r=None

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


    def redis_client_init(self):
        if self.r is None:
            self.r =redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT,password=REDIS_PASSWORD,decode_responses=False,db=0)

    def send_redis(self,data_list,key):
        self.redis_client_init()
        obj = json.dumps(data_list,ensure_ascii=False)

        try:
            self.r.set(key,obj)
            ret = self.r.expire(key,60) # 60秒过期
            print(ret)
        except Exception as e:
            print(e)
            self.r = None
            self.redis_client_init()
            self.r.set(key,obj)
            ret = self.r.expire(key,60)
            print(ret)


    def once(self):
        result =self.fetch_data()
        t = threading.Thread(target=self.send_redis, args=(result,REDIS_KEY))
        t.start()
        t.join()
        print('done')
    def fetch_data(self):
        ret = self.get()

        if not ret:
            time.sleep(5)

        result = []
        for tmp_item in ret.get('rows', []):
            item = tmp_item.get('cell', {})
            bond_nm = item.get('bond_nm', '').strip()
            bond_id = item.get('bond_id', '').strip()

            full_price = round(item.get('price'), 2)
            premium_rt = item.get('premium_rt')

            sincrease_rt = item.get('sincrease_rt')  # 正股涨幅
            increase_rt = item.get('increase_rt')
            curr_iss_amt = round(item.get('curr_iss_amt'), 2)  # 剩余规模
            flag = item.get('redeem_icon')
            pb = item.get('pb')
            list_dt = item.get('list_dt')
            convert_value = item.get('convert_value')
            convert_price = item.get('convert_price')
            tmp_dict = {'bond_nm': bond_nm, 'bond_id': bond_id, 'zz_price': full_price,
                        'premium_rt': premium_rt, 'sincrease_rt': sincrease_rt, 'increase_rt': increase_rt,
                        'curr_iss_amt': curr_iss_amt, 'flag': flag, 'pb': pb, 'list_dt': list_dt,
                        'convert_value': convert_value, 'convert_price': convert_price

                        }

            result.append(tmp_dict)

        return result

    def realtime_fetch(self):

        while True:
            # if True:
            if self.trading_time() == 0:
                self.fetch_data()
            elif self.trading_time() == 1:
                break

            time.sleep(ACCESS_INTERVAL_REALTIME)

    def monitor(self):

        while True:

            # if True:
            if self.trading_time() == 0:
                ret = self.get()

                if not ret:
                    self.logger.error('数据为空，网络问题')
                    time.sleep(5)
                    continue

                for body_dict in ret.get('rows', []):
                    item = body_dict.get('cell', {})

                    bond_nm = item.get('bond_nm', '').strip()
                    bond_id = item.get('bond_id', '').strip()

                    full_price = round(item.get('price'),1)
                    premium_rt = item.get('premium_rt')

                    sincrease_rt = item.get('sincrease_rt')  # 正股涨幅

                    if sincrease_rt is None:
                        # 正股停牌了
                        continue

                    increase_rt = item.get('increase_rt')
                    curr_iss_amt = round(item.get('curr_iss_amt'),2)  # 剩余规模
                    word = '涨停 ' if sincrease_rt > 0 else '跌停'

                    flag = item.get('redeem_icon')
                    if FILTER_REDEEM and (flag in ['Y','0','R','O']):
                        #过滤强赎
                        continue

                    if curr_iss_amt>=REMAIN_SIZE:
                        # 过滤规模大于15亿
                        continue

                    if abs(increase_rt) > ZZ_PERCENT and self.history.is_expire(bond_id):
                        text = f'{bond_nm} {increase_rt},价格：{full_price}; 正股{sincrease_rt}; 规模：{curr_iss_amt}; 溢价率：{premium_rt}'
                        t = threading.Thread(target=self.notify, args=(text,))
                        t.start()
                        self.history.add(bond_id)

                    if abs(sincrease_rt) >= ZG_PERCENT and self.history.is_expire(bond_id):
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
    # app.once()