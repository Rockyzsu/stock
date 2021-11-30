# -*- coding: utf-8 -*-
# @Time : 2021/11/2 22:36
# @File : xueqiu_sync_portfolio.py
# @Author : Rocky C@www.30daydo.com

# 自动同步券商持仓到雪球的组合

import pandas as pd
import json
import requests
import warnings

warnings.filterwarnings("ignore")

cookie = 'device_id=6aee0a85f5b48e54b1223eeb3178dac8; s=c0123vd16e; bid=a8ec0ec01035c8be5606c595aed718d4_ktd4c627; remember=1; xq_a_token=e4ca5c31b277a047685775b19d5fd3d2ab7b2f84; xqat=e4ca5c31b277a047685775b19d5fd3d2ab7b2f84; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjE3MzM0NzM0ODAsImlzcyI6InVjIiwiZXhwIjoxNjM4MDI2ODQwLCJjdG0iOjE2MzU3NDEwOTE2NzEsImNpZCI6ImQ5ZDBuNEFadXAifQ.mjHsfKoyP0Wrr_aWYWUp1_x2mtR-n_0uoIf7-PuZml5BsR8rOZDScdJ0BPiiuknreQsIFPl4k0h_tv3tXNVOwkZTYgaVoygikZrFS86DfHiCBLx1erhEPmn2KqXzm__eZBTys_f1Djh97Ue6w37em_2EeaP3LuVToxkPGhA45uFdHnf63SXQ8i6VSptjLAPMOcaZ6jCZvCVNHfCIJBvTow_kBMu8lbaucb9VspG26EdsXNLQvp61E7srNlRpZUEHuKezzFGWNtlrLtGsXfGRbHD6ZF7GK6aK72FMx1ouAnJzdCoxwqNIYjqycgBb1S0_GA4qq1PTXSAJwcYeRvDa2w; xq_r_token=b77291b9e64bbde68fe9a15d88f16bec2a004d26; xq_is_login=1; u=1733473480; Hm_lvt_fe218c11eab60b6ab1b6f84fb38bcc4a=1635746829; Hm_lvt_1db88642e346389874251b5a1eded6e3=1634120615,1635687700,1635741084,1635774204; snbim_minify=true; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1635865829'
gid = '4320844764546540'


def trade_record(cookie, data):
    url = 'https://tc.xueqiu.com/tc/snowx/MONI/transaction/add.json'

    header = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-length': '104',
        'content-type': 'application/x-www-form-urlencoded',
        'cookie': cookie,
        'origin': 'https://xueqiu.com',
        'referer': 'https://xueqiu.com/performance',
        'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    resp = requests.post(url, data=data, headers=header, verify=False)
    content = resp.content.decode(resp.encoding)

    data_dict = json.loads(content)
    success = data_dict['success']

    name = data_dict['result_data']['name']
    price = data_dict['result_data']['price']
    direction = "卖出" if data_dict['result_data']['type'] == 2 else "买入"

    shares = data_dict['result_data']['shares']
    msg = data_dict['msg']
    # print(data_dict)
    print("{}：以 {} {} {}，{}".format(name, price, direction, shares, msg))
    return success


def history_trade(se, cookie, tableid):
    trade_type = '2' if se['委托类别'] == '卖出' else '1'
    tradedate = str(se['成交日期'])

    date = '{}-{}-{}'.format(tradedate[:4], tradedate[4:6], tradedate[6:8])
    symbol = 'SH' if se['股东代码'][0] == 'A' else 'SZ'
    symbol += str(se['证券代码'])
    price = se['成交价格']
    shares = se['成交数量'] * 10 if se['股东代码'][0] == 'A' else se['成交数量']

    commission = se['佣金']

    data = {
        'type': trade_type,  # 1 买入 2 卖出
        'date': date,
        'gid': tableid,
        'symbol': symbol,
        'price': price,
        'shares': shares,
        'commission': commission
    }
    success = trade_record(cookie, data)
    return data


def main():


    history_trade_info_df = pd.read_excel('例子.xlsx')

    print(history_trade_info_df.head())
    history_trade_info_df['success'] = history_trade_info_df.apply(lambda x: history_trade(x, cookie, gid), axis=1)
    print("失败个数：{}".format(len(history_trade_info_df[history_trade_info_df['success'] == False])))
    print(history_trade_info_df[history_trade_info_df['success'] == False])


if __name__ == '__main__':
    main()
