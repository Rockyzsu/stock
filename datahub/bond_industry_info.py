# -*- coding: utf-8 -*-
# @Time : 2021/8/9 11:56
# @File : bond_industry_info.py
# @Author : Rocky C@www.30daydo.com
import datetime
import os
from joblib import dump
import parsel

from datahub.jsl_login import login
from configure.settings import config
import time

headers = {
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Host": "www.jisilu.cn",
    "Origin": "https://www.jisilu.cn",
    "Referer": "https://www.jisilu.cn/data/cbnew/",
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}


class BondIndustry:

    def __init__(self):
        self.today = datetime.date.today().strftime('%Y%m%d')

    def run(self):
        name_value = self.parse_selection_id()
        session = self.get_session()
        df_dict = {}
        for name, value in name_value:
            result = self.get_bond_info(session, value)
            df_dict[name] = result
        dump(df_dict, f'industry_{self.today}.pkl')

    def get_session(self):
        return login(config['jsl_monitor']['JSL_USER'], config['jsl_monitor']['JSL_PASSWORD'])

    def get_bond_info(self, session, industry_id):
        ts = int(time.time() * 1000)
        url = 'https://www.jisilu.cn/data/cbnew/cb_list/?___jsl=LST___t={}'.format(ts)
        data = {
            "fprice": None,
            "tprice": None,
            "curr_iss_amt": None,
            "volume": None,
            "svolume": None,
            "premium_rt": None,
            "ytm_rt": None,
            "rating_cd": None,
            "is_search": 'R',
            "btype": None,
            "listed": 'Y',
            "qflag": 'N',
            "sw_cd": industry_id,
            "bond_ids": None,
            "rp": 50
        }

        r = session.post(
            url=url,
            headers=headers,
            data=data
        )
        ret = r.json()
        result = []
        for item in ret['rows']:
            result.append(item['cell'])
        return result

    def parse_data(self, data):
        pass

    def parse_selection_id(self):
        parent = os.path.dirname(__file__)
        file = os.path.join(parent, 'selection.html')
        with open(file, 'r', encoding='utf8') as f:
            content = f.read()
        resp = parsel.Selector(text=content)
        nodes = resp.xpath('//option[@data-level="1"]')
        result_list = []
        for nod in nodes:
            value = nod.xpath('.//@value').extract_first()
            name = nod.xpath('.//text()').extract_first()
            name = name.split('(')[0]
            result_list.append((name, int(value)))
        return result_list


def main():
    app = BondIndustry()
    app.run()


if __name__ == '__main__':
    main()
