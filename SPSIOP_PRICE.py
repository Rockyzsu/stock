# -*-coding=utf-8-*-

# @Time : 2019/10/20 23:14
# @File : SPSIOP_PRICE.py
# 获取SPSIOP的价格，每天早上美股收盘
import datetime

import requests
import pymongo
from settings import send_aliyun, llogger,QQ_MAIL

client = pymongo.MongoClient('192.168.10.48', 17001)
doc = client['db_stock']['SPSIOP']
# 先访问一下雪球首页得到cookies
logger = llogger('log/huabaoyouqi.log')

home_headers = {'User-Agent': 'Xueqiu App'}

headers = {'User-Agent': 'Xueqiu App',
           'Access-Control-Allow-Origin': 'https://xueqiu.com',
           'Content-Type': 'application/json;charset=UTF-8',
           'P3P': 'CP="IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR IND CNT"'}
url = 'https://stock.xueqiu.com/v5/stock/quote.json?symbol=.SPSIOP&extend=detail'
home_page = 'https://xueqiu.com'
today = datetime.datetime.now().strftime('%Y-%m-%d')


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
    ret = qdii_info()
    if ret:
        predict_v = round((1+percent*0.95*0.01)*ret,3)
        logger.info(f'最新估值{predict_v}')
        d={'日期':today,'估值':predict_v}
        client['db_stock']['huabaoyouqi_predict'].insert_one(d)
        title=f'{today}华宝估值{predict_v}'
        send_aliyun(title,'',QQ_MAIL)
    else:

        logger.error('获取估值失败')



def qdii_info():
    url = 'https://www.jisilu.cn/data/qdii/qdii_list/?rp=25&page=1'
    r = requests.get(url=url, headers=home_headers)
    js_data = r.json()
    rows = js_data.get('rows', [])
    new_rows=[]
    for row in rows:
        new_rows.append(row.get('cell'))
    doc = client['DB_QDII'][today]

    try:
        doc.insert(new_rows)

    except Exception as e:
        logger.error(e)
    else:
        for row in rows:
            if row.get('cell', {}).get('fund_nm') == '华宝油气':

                nav = row.get('cell', {}).get('fund_nav')
                try:
                    nav = float(nav)  # 网站给的是字符
                except:
                    return None
                else:
                    return nav


if __name__ == '__main__':
    get_price()
