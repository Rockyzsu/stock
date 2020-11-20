# -*-coding=utf-8-*-

# @Time : 2020/1/20 10:54
# @File : realtime_price.py
import pypinyin
import time
import requests
import sys
sys.path.append('..')
from configure.util import read_web_headers_cookies

__doc__='''
命令行下替代网页版查询实时可转债数据
'''

session = requests.Session()

headers, cookies = read_web_headers_cookies('jsl',headers=True, cookies=False)

ts = int(time.time() * 1000)
params = (
    ('___jsl', f'LST___t={ts}'),
)

data = {
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

while 1:
    name = input('input name => ')
    if name == 'q':
        print('退出')
        break
    try:
        response = session.post('https://www.jisilu.cn/data/cbnew/cb_list/', headers=headers, params=params,
                                cookies=cookies, data=data, timeout=3)
    except Exception as e:
        print(e)
        continue

    ret = response.json()

    for body_dict in ret.get('rows', []):
        item = body_dict.get('cell', {})
        bond_nm = item.get('bond_nm', '').strip()
        a = pypinyin.pinyin(bond_nm, style=pypinyin.FIRST_LETTER)

        b = []
        for i in range(len(a)):
            b.append(str(a[i][0]).lower())
        c = ''.join(b)

        if name == c:
            full_price = item.get('full_price')
            remium_rt = item.get('premium_rt')
            increase_rt = item.get('increase_rt')
            sincrease_rt = item.get('sincrease_rt')

            print('name ==>', bond_nm.replace('转债', ''))
            print('price ==>', full_price)
            print('pecent ==>', increase_rt)
            print('溢价率 ==>', remium_rt)
            print('正骨percent ==>', sincrease_rt)
            print('\n')
