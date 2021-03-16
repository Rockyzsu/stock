# 使用jsl作为数据源
import requests
import sys
sys.path.append('..')
import time
import threading
from configure.settings import market_status, config
from common.BaseService import BaseService,HistorySet
from configure.util import read_web_headers_cookies

ACCESS_INTERVAL = config['jsl_monitor']['ACCESS_INTERVAL']
MONITOR_PERCENT = config['jsl_monitor']['MONITOR_PERCENT']
EXPIRE_TIME = config['jsl_monitor']['EXPIRE_TIME']


class ReachTargetJSL(BaseService):
    def __init__(self):
        super(ReachTargetJSL, self).__init__(f'../log/{self.__class__.__name__}.log')
        self.session = requests.Session()
        self.__headers , self.cookies = read_web_headers_cookies('jsl',headers=True,cookies=False)
        ts = int(time.time()*1000)
        self.params = (
            ('___jsl', f'LST___t={ts}'),
        )

        self.query_condition = {
            'fprice': '',
            'tprice': '',
            'volume': '',
            'svolume': '',
            'premium_rt': '',
            'ytm_rt': '',
            'rating_cd': '',
            'is_search': 'Y',
            'btype': 'C',
            'listed': 'Y',
            'sw_cd': '',
            'bond_ids': '',
            'rp': '50'
        }

        self.history = HistorySet(expire=EXPIRE_TIME)

    def get(self,*args,**kwargs):
        # 复写
        try:
            response = self.session.post('https://www.jisilu.cn/data/cbnew/cb_list/', headers=self.__headers,
                                         params=self.params,
                                         cookies=self.cookies, data=self.query_condition, timeout=30)
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

            if self.trading_time() == 0:
                ret = self.get()

                if not ret:
                    time.sleep(5)
                    continue

                for body_dict in ret.get('rows', []):
                    item = body_dict.get('cell', {})
                    bond_nm = item.get('bond_nm', '').strip()
                    bond_id = item.get('bond_id', '').strip()

                    full_price = item.get('full_price')
                    premium_rt = self.__convert__(item.get('premium_rt'))

                    sincrease_rt = item.get('sincrease_rt')  # 正股涨幅
                    sincrease_rt = self.__convert__(sincrease_rt)

                    increase_rt = item.get('increase_rt')
                    curr_iss_amt = self.__convert__(item.get('curr_iss_amt'))  # 剩余规模
                    word = '涨停 'if sincrease_rt>0 else '跌停'

                    if abs(sincrease_rt) >= MONITOR_PERCENT and self.history.is_expire(bond_id):
                        str_content = '负' + increase_rt if float(increase_rt.replace('%', '')) < 0 else increase_rt
                        str_content = str_content.replace('%', '')
                        text = f'{bond_nm[:2]}-债{str_content}-股{sincrease_rt}-规模{curr_iss_amt}-溢{premium_rt}'
                        t = threading.Thread(target=self.notify, args=(text,))
                        t.start()
                        self.logger.info(f'{bond_nm} {word}')
                        self.history.add(bond_id)

            elif self.trading_time()==1:
                break
            else:
                pass

            time.sleep(ACCESS_INTERVAL)
