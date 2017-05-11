# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
import requests
class Jubi_web():

    def __init__(self):
        pass

    def getContent(self):
        url='https://www.jubi.com/api/v1/trade_list'

        params_data={'key':'7a9wc-t3pkx-7snvp-3yb7w-m86g6-u5896-4ffcc','signature':}
        s=requests.get(url=url,params=params_data)