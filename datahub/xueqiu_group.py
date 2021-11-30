# -*- coding: utf-8 -*-
# @Time : 2021/11/2 23:25
# @File : xueqiu_group.py
# @Author : Rocky C@www.30daydo.com
import json

import requests


def main():
    url = 'https://xueqiu.com/cubes/rebalancing/create.json'
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "__utmz=1.1624412177.48.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; device_id=6aee0a85f5b48e54b1223eeb3178dac8; s=c0123vd16e; bid=a8ec0ec01035c8be5606c595aed718d4_ktd4c627; remember=1; xq_a_token=e4ca5c31b277a047685775b19d5fd3d2ab7b2f84; xqat=e4ca5c31b277a047685775b19d5fd3d2ab7b2f84; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjE3MzM0NzM0ODAsImlzcyI6InVjIiwiZXhwIjoxNjM4MDI2ODQwLCJjdG0iOjE2MzU3NDEwOTE2NzEsImNpZCI6ImQ5ZDBuNEFadXAifQ.mjHsfKoyP0Wrr_aWYWUp1_x2mtR-n_0uoIf7-PuZml5BsR8rOZDScdJ0BPiiuknreQsIFPl4k0h_tv3tXNVOwkZTYgaVoygikZrFS86DfHiCBLx1erhEPmn2KqXzm__eZBTys_f1Djh97Ue6w37em_2EeaP3LuVToxkPGhA45uFdHnf63SXQ8i6VSptjLAPMOcaZ6jCZvCVNHfCIJBvTow_kBMu8lbaucb9VspG26EdsXNLQvp61E7srNlRpZUEHuKezzFGWNtlrLtGsXfGRbHD6ZF7GK6aK72FMx1ouAnJzdCoxwqNIYjqycgBb1S0_GA4qq1PTXSAJwcYeRvDa2w; xq_r_token=b77291b9e64bbde68fe9a15d88f16bec2a004d26; xq_is_login=1; u=1733473480; Hm_lvt_fe218c11eab60b6ab1b6f84fb38bcc4a=1635746829; Hm_lvt_1db88642e346389874251b5a1eded6e3=1634120615,1635687700,1635741084,1635774204; snbim_minify=true; __utma=1.108610398.1599525840.1635746825.1635864334.64; __utmc=1; acw_tc=2760826c16358660203771708eb6350cdbef341a109ef5e615ee6850a612b1; __utmt=1; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1635866525; __utmb=1.14.10.1635864334",
        "Host": "xueqiu.com",
        "Origin": "https://xueqiu.com",
        "Pragma": "no-cache",
        "Referer": "https://xueqiu.com/p/update?action=holdings&symbol=ZH2333460",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    data = {"cube_symbol": "ZH2333460",
            "cash": 41.94-33,
            "segment": True,
            "holdings": [{"stock_id": 1027747, "weight": 1.06, "segment_name": "其他", "segment_id": 11097508,
                          "stock_name": "港股通银行LOF", "stock_symbol": "SH501025", "segment_color": "#0055aa",
                          "proactive": False, "volume": 0.01096467, "textname": "港股通银行LOF(SH501025)",
                          "url": "/S/SH501025", "price": 0.953, "percent": -0.73, "flag": 1},

                         {"stock_id": 1032085, "weight": 13, "segment_name": "可转债", "segment_id": 13493397,
                          "stock_name": "山鹰转债", "stock_symbol": "SH110047", "segment_color": "#e53e1e",
                          "proactive": True, "volume": 0.00110456, "textname": "山鹰转债(SH110047)", "url": "/S/SH110047",
                          "price": 116.02, "percent": -0.42, "flag": 1},

                         {"chg": -0.045, "code": "SZ127003", "current": 108.055, "flag": 1, "ind_color": "#0055aa",
                          "ind_id": 0, "ind_name": "可转债", "name": "海印转债", "percent": -0.04, "stock_id": 1026908,
                          "textname": "海印转债(SZ127003)", "segment_name": "可转债", "weight": 22, "url": "/S/SZ127003",
                          "proactive": True, "price": 108.055},

                         # {"chg": -0.48, "code": "SZ128044", "current": 99.42, "flag": 1, "ind_color": "#0055aa",
                         #  "ind_id": 0, "ind_name": "可转债", "name": "岭南转债", "percent": -0.48, "stock_id": 1031329,
                         #  "textname": "岭南转债(SZ128044)", "segment_name": "可转债", "weight": 22, "url": "/S/SZ128044",
                         #  "proactive": True, "price": 99.42},

                         # {"chg": 1.94, "code": "SZ128046", "current": 143, "flag": 1, "ind_color": "#0055aa",
                         #  "ind_id": 0, "ind_name": "可转债", "name": "利尔转债", "percent": -0.48, "stock_id": 1031329,
                         #  "textname": "利尔转债(SZ128046)", "segment_name": "可转债", "weight": 33, "url": "/S/SZ128046",
                         #  "proactive": True, "price": 143}
                         ],
            "comment": None}

    # r = requests.post(url, data=data,headers=headers)
    r = requests.post(url, json=data,headers=headers)
    r.encoding='utf8'
    print(r.text)


if __name__ == '__main__':
    main()
