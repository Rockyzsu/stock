# -*- coding: utf-8 -*-
# @Time : 2021/7/26 15:59
# @File : jsl_login.py
# @Author : Rocky C@www.30daydo.com


import datetime
import time
import pandas as pd
import execjs
import os
import requests
import sys

sys.path.append('..')
from configure.settings import config

filename = 'js_file/encode_jsl.js'

path = os.path.dirname(os.path.abspath(__file__))
full_path = os.path.join(path, filename)

headers = {
    'Host': 'www.jisilu.cn', 'Connection': 'keep-alive', 'Pragma': 'no-cache',
    'Cache-Control': 'no-cache', 'Accept': 'application/json,text/javascript,*/*;q=0.01',
    'Origin': 'https://www.jisilu.cn', 'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0(WindowsNT6.1;WOW64)AppleWebKit/537.36(KHTML,likeGecko)Chrome/67.0.3396.99Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
    'Referer': 'https://www.jisilu.cn/login/',
    'Accept-Encoding': 'gzip,deflate,br',
    'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8'
}


def decoder(text):
    with open(full_path, 'r', encoding='utf8') as f:
        source = f.read()

    ctx = execjs.compile(source)
    key = '397151C04723421F'
    return ctx.call('jslencode', text, key)




def get_bond_info(session):
    ts = int(time.time() * 1000)
    url = 'https://www.jisilu.cn/data/cbnew/cb_list_new/?___jsl=LST___t={}'.format(ts)
    data = {
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


def login(user, password):
    session = requests.Session()
    url = 'https://www.jisilu.cn/account/ajax/login_process/'
    username = decoder(user)
    jsl_password = decoder(password)
    data = {
        'return_url': 'https://www.jisilu.cn/',
        'user_name': username,
        'password': jsl_password,
        'net_auto_login': '1',
        '_post_type': 'ajax',
    }

    js = session.post(
        url=url,
        headers=headers,
        data=data,
    )

    ret = js.json()
    if ret.get('errno') == 1:
        print('登录成功')
        return session
    else:
        print('登录失败')
        raise ValueError('登录失败')


def main():
    today = datetime.datetime.now().strftime('%Y%m%d')
    user = config['jsl_monitor']['JSL_USER']
    password = config['jsl_monitor']['JSL_PASSWORD']
    session = login(user, password)
    ret = get_bond_info(session)
    df = pd.DataFrame(ret)
    # print(df)
    return df


if __name__ == '__main__':
    main()
