# -*- coding: utf-8 -*-
# @Time : 2020/11/16 11:37
# @File : util.py
# @Author : Rocky C@www.30daydo.com
import requests
from .settings import config, get_config_data


def notify(title='', desp=''):
    url = f"https://sc.ftqq.com/{config['WECHAT_ID']}.send?text={title}&desp={desp}"
    try:
        res = requests.get(url, timeout=5)
    except Exception as e:
        print(e)
        return False

    else:
        try:
            js = res.json()
            result = True if js['data']['errno'] == 0 else False
            if result:
                print('发送成功')
                return True
            else:
                print('发送失败')
                return False

        except Exception as e:
            print(e)
            print(res.text)


def read_web_headers_cookies(website, headers=False, cookies=False):
    config = get_config_data('web_headers.json')
    return_headers = None
    return_cookies = None

    if headers:
        return_headers = config[website]['headers']

    if cookies:
        return_cookies = config[website]['cookies']

    return return_headers, return_cookies
