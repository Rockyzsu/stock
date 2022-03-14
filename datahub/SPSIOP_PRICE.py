# -*-coding=utf-8-*-

# @Time : 2019/10/20 23:14
# @File : SPSIOP_PRICE.py
# 获取SPSIOP的价格，每天早上美股收盘
# 先获取xop的前一天的涨幅，然后在前一天华宝油气的基础上相加
import sys
sys.path.append('..')
import datetime
import requests
from common.BaseService import BaseService
from configure.util import send_from_aliyun
from configure.settings import DBSelector


DB = DBSelector()
client = DB.mongo(location_type='qq',async_type=False)

doc = client['db_stock']['SPSIOP']

# 先访问一下雪球首页得到cookies

home_headers = {'User-Agent': 'Xueqiu App'}
headers = {'User-Agent': 'Xueqiu App',
           'Access-Control-Allow-Origin': 'https://xueqiu.com',
           'Content-Type': 'application/json;charset=UTF-8',
           'P3P': 'CP="IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR IND CNT"'}

xueqiu_url = 'https://stock.xueqiu.com/v5/stock/quote.json?symbol=.SPSIOP&extend=detail'
home_page = 'https://xueqiu.com'

today = datetime.datetime.now().strftime('%Y-%m-%d')

class SPSIOP(BaseService):

    def __init__(self):
        super(SPSIOP, self).__init__('../log/huabaoyouqi.log')

    def predict_price(self):

        session = requests.Session()
        session.get(url=home_page, headers=home_headers)

        r = session.get(url=xueqiu_url,
                        headers=headers)

        js_data = r.json()

        quote = js_data.get('data', {}).get('quote')

        quote['crawltime'] = datetime.datetime.now()
        doc.insert_one(quote)
        percent = quote.get('percent')
        jsl_qdii,est_val_dt = self.qdii_info()

        if jsl_qdii:
            predict_v = round((1 + percent * 0.95 * 0.01) * jsl_qdii, 3)
            self.logger.info(f'最新估值{predict_v}')
            d = {'日期': today, '估值': predict_v}
            client['db_stock']['huabaoyouqi_predict'].insert_one(d)
            title = f'华宝估值{predict_v} 净值日期{est_val_dt[5:]}'
            send_from_aliyun(title, '')

        else:
            self.notify(title='华宝油气获取估值失败')


    def qdii_info(self):
        url = 'https://www.jisilu.cn/data/qdii/qdii_list/?rp=25&page=1'
        r = requests.get(url=url, headers=home_headers)
        js_data = r.json()
        rows = js_data.get('rows', [])
        new_rows = []
        for row in rows:
            new_rows.append(row.get('cell'))
        doc_ = client['DB_QDII'][today]

        try:
            doc_.insert_many(new_rows)

        except Exception as e:
            self.logger.error(e)

        next_url = 'https://www.jisilu.cn/data/qdii/qdii_list/C?___jsl=LST___t=1604513012662&rp=22'
        r = requests.get(url=next_url, headers=home_headers)
        js_data = r.json()
        rows = js_data.get('rows', [])

        for row in rows:
            if row.get('cell', {}).get('fund_nm') == '华宝油气':

                nav = row.get('cell', {}).get('fund_nav')
                est_val_dt = row.get('cell', {}).get('est_val_dt')

                try:
                    nav = float(nav)  # 网站给的是字符
                except:
                    return None
                else:
                    return nav,est_val_dt


def main():
    spider = SPSIOP()
    spider.predict_price()

if __name__ == '__main__':
    main()