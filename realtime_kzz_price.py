# -*-coding=utf-8-*-

# @Time : 2020/1/20 10:54
# @File : realtime_price.py
import pypinyin
import requests
session = requests.Session()
cookies = {
    'auto_reload': 'true',
    'kbzw_r_uname': '%E9%87%8F%E5%8C%96%E8%87%AA%E7%94%B1%E4%B9%8B%E8%B7%AF',
    'kbz_newcookie': '1',
    'kbzw__Session': '1kmak8h8v6pscf5brjllb9hfk3',
    'Hm_lvt_164fe01b1433a19b507595a43bf58262': '1578275141,1578879529',
    'Hm_lpvt_164fe01b1433a19b507595a43bf58262': '1579488732',
}

headers = {
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

params = (
    ('___jsl', 'LST___t=1579488785838'),
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
    if name=='q':
        print('退出')
        break
    try:
        response = session.post('https://www.jisilu.cn/data/cbnew/cb_list/', headers=headers, params=params, cookies=cookies, data=data,timeout=3)
    except:
        print('网络超时')
        continue
        
    ret = response.json()

    for body_dict in ret.get('rows',[]):
        # print(item)
        item=body_dict.get('cell',{})
        bond_nm = item.get('bond_nm','').strip()
        a=pypinyin.pinyin(bond_nm, style=pypinyin.FIRST_LETTER)

        b = []
        for i in range(len(a)):
            b.append(str(a[i][0]).lower())
        c = ''.join(b)

        if name == c:
            full_price=item.get('full_price')
            remium_rt=item.get('premium_rt')
            increase_rt=item.get('increase_rt')

            print('name ==>',bond_nm.replace('转债',''))
            print('price ==>',full_price)
            print('pecent ==>',increase_rt)
            print('yjl ==>',remium_rt)
            print('\n')

