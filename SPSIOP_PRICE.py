# -*-coding=utf-8-*-

# @Time : 2019/10/20 23:14
# @File : SPSIOP_PRICE.py
# 获取SPSIOP的价格，每天早上美股收盘
import datetime

import requests
import pymongo
from settings import s
client = pymongo.MongoClient('192.168.10.48', 17001)
doc = client['db_stock']['SPSIOP']
# 先访问一下雪球首页得到cookies

home_headers = {'User-Agent': 'Xueqiu App'}

headers = {'User-Agent': 'Xueqiu App',
           'Access-Control-Allow-Origin': 'https://xueqiu.com',
           'Content-Type': 'application/json;charset=UTF-8',
           'P3P': 'CP="IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR IND CNT"'}
url = 'https://stock.xueqiu.com/v5/stock/quote.json?symbol=.SPSIOP&extend=detail'
home_page = 'https://xueqiu.com'



def get_price():
    session = requests.Session()

    session.get(url=home_page, headers=home_headers)

    r = session.get(url=url,
                     headers=headers)

    js_data = r.json()

    quote = js_data.get('data', {}).get('quote')

    quote['crawltime'] = datetime.datetime.now()
    doc.insert_one(quote)
    percent = quote.get('percent')

    # current = quote.get('current')
    # low52w = quote.get('low52w')
    # high52w = quote.get('high52w')
    # amplitude = quote.get('amplitude')
    # d={}
    # d['']


def qdii_info():
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    url='https://www.jisilu.cn/data/qdii/qdii_list/?rp=25&page=1'
    r=requests.get(url=url,headers=home_headers)
    js_data=r.json()
    rows = js_data.get('rows',[])
    doc=client['DB_QDII'][today]
    try:
        doc.insert(rows)
    except Exception as e:
        print(e)
    else:


if __name__ == '__main__':
    get_price()
