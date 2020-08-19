# 使用jsl作为数据源
import requests
import time
import config
from history_set import HistorySet
import threading
from settings import llogger, market_status, send_sms


class ReachTargetJSL():
    def __init__(self):

        self.logger = llogger('jsl_monitor')
        self.session = requests.Session()
        self.cookies = config.jsl_cookies

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
        self.history = HistorySet()

    def get(self):
        try:
            response = self.session.post('https://www.jisilu.cn/data/cbnew/cb_list/', headers=self.headers, params=self.params,
                                         cookies=self.cookies, data=self.data, timeout=30)
        except Exception as e:
            self.logger.error(e)
            return None
        else:
            ret = response.json()
            return ret

    def __convert__(self, string):

        string = string.replace('%', '')
        try:
            string = float(string)
        except:
            return 0
        else:
            return string

    def monitor(self):

        while market_status():
            ret = self.get()
            if not ret:
                time.sleep(5)
                continue

            for body_dict in ret.get('rows', []):
                item = body_dict.get('cell', {})
                bond_nm = item.get('bond_nm', '').strip()
                bond_id = item.get('bond_id', '').strip()

                full_price = item.get('full_price')
                remium_rt = item.get('premium_rt')

                sincrease_rt = item.get('sincrease_rt')
                sincrease_rt = self.__convert__(sincrease_rt)

                increase_rt = item.get('increase_rt')

                if abs(sincrease_rt) >= config.MONITOR_PERCENT and self.history.is_expire(bond_id):
                    '''
                    发送消息
                    t = threading.Thread(target=show_box, args=(bond_nm,))
                    t.start()
                    '''
                    text = f'{bond_id}{bond_nm} 异动，转债涨幅：{increase_rt}'
                    t = threading.Thread(target=send_sms, args=(text,))
                    t.start()
                    self.logger.info(f'{bond_nm} 涨停')
                    self.history.add(bond_id)

            time.sleep(config.ACCESS_INTERVAL)

    def send_msg(self, text):
        url = f"https://sc.ftqq.com/{config.WECHAT_ID}.send?text=" + text
        res = requests.get(url)
        # send_sms(text)
