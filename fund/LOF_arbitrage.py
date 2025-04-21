# LOF 折价套利
import datetime

import demjson
import fire
import pandas as pd
import requests
import sys

sys.path.append('..')
from configure.settings import DBSelector
from configure.util import send_message_via_wechat
import akshare as ak
from parsel import Selector

TARGET_PREMIUM = 4  # 溢价率阈值


class LOF_arbitrage:
    def __init__(self, save):
        self.db = DBSelector().mongo()
        self.client = self.db['FUND_LOF']
        self.save = save

    def update_premiun(self):
        date = datetime.datetime.now().strftime('%Y-%m-%d')
        doc = self.client[date]
        for fund in doc.find():
            price = float(fund['trade'])
            try:
                netvalue = float(fund['单位净值'])
                discount = (price - netvalue) / netvalue * 100
                doc.update_one({'symbol': fund['symbol']}, {'$set': {"溢价率": discount}})
            except Exception as e:
                print(e)
                print(fund['symbol'], 'error')

    def get_realtime_time(self):
        result = []
        for p in range(1, 11):
            fund_list = self.get_page(p)
            for fund in fund_list:
                symbol = fund['symbol'][2:]

                detail_dict = self.fund_detail(symbol)
                # if detail_dict is None:

                fund.update(detail_dict)
                fund['update_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                try:
                    price = float(fund['trade'])
                    netvalue = float(fund['单位净值'])
                    discount = (price - netvalue) / netvalue * 100
                    fund['溢价率'] = discount
                    # if self.save:
                    #     self.dump_mongodb(fund)
                    result.append(fund)
                except Exception as e:
                    print(e)
                    print(fund['symbol'], 'error')

        return result

    def dump_mongodb(self, data):
        doc = datetime.datetime.now().strftime('%Y-%m-%d')
        self.client[doc].insert_many(data)

        # for d in data:
        #     # print(d)
        #     try:
        #         self.client[doc].insert_one(d)
        #     except Exception as e:
        #         print(e)
        #         print(d)

    def fund_detail(self, code):

        url = "https://finance.sina.com.cn/fund/quotes/{}/bc.shtml".format(code)

        payload = {}
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6',
            'cache-control': 'max-age=0',
            'cookie': 'U_TRS1=000000c2.925a2b81b.6558bdf3.97ea41e9; UOR=www.baidu.com,news.sina.com.cn,; SINAGLOBAL=120.241.117.235_1703000974.412329; vjuids=4c66e81c3.18cb039b64b.0.cef1458c27042; vjlast=1703763621; FSINAGLOBAL=120.241.117.235_1703000974.412329; SGUID=1703763634913_98154771; SCF=ArSVPydg8FhlTshG00H2EBHL6mTj5KvjUDue6NrOKUJta7f5nCXUBfgx6x6d513NYw6kT6IX8Unv1jxiIcmlWkE.; cna=7f96a3ef4a46413f825435c379c93489; SUB=_2AkMRvjPvf8NxqwFRmfoUzGLlbo1_zg7EieKn4sI0JRMyHRl-yD8XqmoltRB6Oj4dAM5tocrU5gzIUBNaPjqCghlRrMJS; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9WFHrnxo4Wyz.jlo6OcrHRj3; U_TRS2=00000075.2af01df6.66ff7ec7.99627456; display=hidden; Apache=223.160.226.117_1728020174.788833; sinaH5EtagStatus=y; ULV=1728025220573:10:1:1:223.160.226.117_1728020174.788833:1721119235031; visited_funds=501001%7C160637',
            'if-none-match': 'W/"66ff7689-3a07c"V=32179E4F',
            'priority': 'u=0, i',
            'referer': 'http://biz.finance.sina.com.cn/suggest/lookup_n.php?q=sh501001&country=fund',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        if '<meta charset="utf-8"/>' in response.text:
            response.encoding = 'utf-8'
        else:
            response.encoding = 'gb2312'

        result = self.parse(response.text)
        return result

    def parse(self, content):
        xpath_data = Selector(text=content)

        result = {}
        nodes = xpath_data.xpath('//div[@class="fund_data_item"]')
        for node in nodes:
            name = node.xpath('./span[@class="fund_data_tag"]/text()').extract_first()
            value = node.xpath('./span[@class="fund_data"]/text()').extract_first()
            if value is None:
                value = node.xpath('./span[@class="fund_data" or @class="fund_data_green"]/text()').extract_first()

            value = value.replace('%', '').replace('/', '')
            result[name] = value

        if len(result) == 0:
            # 额外解析
            th_node = xpath_data.xpath('//div[@id="fund-hq"]//table//th')
            for node in th_node:
                name = node.xpath('./text()').extract_first()
                value = node.xpath('./span/text()').extract_first()
                name = name.replace('：', '').replace(':', '')
                # if len(td_node)>0:
                #     value = td_node[0].xpath('./text()').extract_first()
                #     result[name] = value
                value = value.replace('%', '')
                # print(name,value)
                if name == '基金简称' or name == '申购状态':
                    continue
                result[name] = value

        return result

    def postfix(self, code):
        if code.starts('5'):
            return 'SH' + code
        else:
            return 'SZ' + code

    def get_page(self, p):

        url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/jsonp.php/IO.XSRV2.CallbackList['BwSgm6CTKGGEoOxP']/Market_Center.getHQNodeDataSimple?page={}&num=40&sort=symbol&asc=1&node=lof_hq_fund&%5Bobject%20HTMLDivElement%5D=etp68".format(
            p)
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.text
        start = data.index('[{')
        end = data.rindex(']')
        data = data[start:end + 1]
        py_object = demjson.decode(data)
        return py_object

    def run(self):
        result = self.get_realtime_time()
        df = pd.DataFrame(result)
        fund_purchase_em_df = ak.fund_purchase_em()
        merge_df = pd.merge(df, fund_purchase_em_df, left_on='code', right_on='基金代码', how='left')
        if self.save:
            merge_df['下一开放日'] = merge_df['下一开放日'].map(lambda x: str(x))
            # merge_df['下一开放日'] = merge_df['下一开放日'].fillna('')
            merge_df['最新净值/万份收益-报告时间'] = merge_df['最新净值/万份收益-报告时间'].map(lambda x: str(x))
            json_data = merge_df.to_dict(orient='records')
            try:
                self.dump_mongodb(json_data)
            except Exception as e:
                send_message_via_wechat('LOF溢价率数据存储失败')
        target_df = merge_df[merge_df['溢价率'] >= TARGET_PREMIUM]

        for index, row in target_df.iterrows():
            code = row['code']
            name = row['基金简称']
            premium = round(float(row['溢价率']), 2)
            status = row['申购状态']
            limit_amount = row['日累计限定金额']
            if status == '暂停申购':
                continue
            _code = self.postfix(code)

            try:
                stock_individual_spot_xq_df = ak.stock_individual_spot_xq(symbol=_code)
                volume = stock_individual_spot_xq_df[stock_individual_spot_xq_df['item'] == '成交额']['value'].iloc[0]
            except Exception as e:
                msg = '{} {} 溢价率 {},{},{}'.format(code, name, premium, status, limit_amount)
                send_message_via_wechat(msg)

            else:
                if volume / 10000 >= 10:  # 大于10万成交额
                    msg = '{} {} 溢价率 {},{},{}，成交量{}'.format(code, name, premium, status, limit_amount, volume)
                    send_message_via_wechat(msg)


def main(save=False):
    today = datetime.datetime.now()
    weekday = today.weekday()

    if weekday == 5 or weekday == 6:
        return

    app = LOF_arbitrage(save)
    app.run()


if __name__ == '__main__':
    fire.Fire(main)
