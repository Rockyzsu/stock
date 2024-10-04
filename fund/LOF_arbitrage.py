# LOF 折价套利
import datetime

import demjson
import requests
import  sys
sys.path.append('..')
from configure.settings import config_dict,DBSelector

class LOF_arbitrage:
    def __init__(self):
        self.db = DBSelector().mongo()
        self.client = self.db['FUND_LOF']

    def get_realtime_time(self):
        for p in range(1, 11):
            fund_list = self.get_page(p)
            for fund in fund_list:
                symbol = fund['symbol'][2:]
                detail_dict = self.fund_detail(symbol)
                saved_dict = fund.copy()
                saved_dict.update(detail_dict)
                self.dump_mongodb(saved_dict)

    def dump_mongodb(self,data):
        doc = datetime.datetime.now().strftime('%Y-%m-%d')
        self.client[doc].insert_one(data)


    def fund_detail(self,code):

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
        response.encoding='utf-8'
        result = self.parse(response.text)
        print(result)

    def parse(self,content):
        from parsel import Selector
        xpath_data =Selector(text=content)
        nodes=xpath_data.xpath('//div[@class="fund_data_item"]')
        result = {}
        for node in nodes:
            name = node.xpath('./span[@class="fund_data_tag"]/text()').extract_first()
            value = node.xpath('./span[@class="fund_data"]/text()').extract_first()
            if value is None:
                value = node.xpath('./span[@class="fund_data" or @class="fund_data_green"]/text()').extract_first()

            value = value.replace('%','').replace('/','')
            result[name] = value
        return result

    def get_page(self,p):

        url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/jsonp.php/IO.XSRV2.CallbackList['BwSgm6CTKGGEoOxP']/Market_Center.getHQNodeDataSimple?page={}&num=40&sort=symbol&asc=1&node=lof_hq_fund&%5Bobject%20HTMLDivElement%5D=etp68".format(p)
        payload = {}
        headers = {}
        response = requests.request("GET", url, headers=headers, data=payload)

        # print(response.text)
        data = response.text
        start = data.index('[{')
        end = data.rindex(']')
        data = data[start:end+1]
        py_object = demjson.decode(data)
        return py_object

    def run(self):
        self.get_realtime_time()
        # self.fund_detail('501001')


if __name__ == '__main__':
    app = LOF_arbitrage()
    app.run()