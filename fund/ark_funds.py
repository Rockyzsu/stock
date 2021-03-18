# Crawl ARK Fund holdings and parse pdf file with python
# 获取ARK持仓数据 python解析pdf

import sys
sys.path.append('..')
import datetime
from parsel import Selector
from common.BaseService import BaseService
from configure.settings import DBSelector

# maxium count to try on save data to mongodb
MAX_COUNT = 5

class ARKFundSpider(BaseService):

    def __init__(self):
        super(ARKFundSpider, self).__init__('../log/ark.log')

        self.url = 'https://ark-funds.com/auto/gettopten.php'
        self.data = {'ticker': None}
        self.doc = self.mongodb()

    def mongodb(self):
        doc=DBSelector().mongo('qq')['db_stock']['ark_fund']
        try:
            doc.create_index([('name',1),('type',1),('date',1)],unique=True)
        except Exception as e:
            print(e)

        return doc
    @property
    def headers(self):
        return {"accept-encoding": "gzip, deflate, br",
                "accept-language": "zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7",
                "cache-control": "no-cache",
                # "content-length": "11",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "cookie":"__cfduid=d6d00b7e7c3e594db5594b2c4cdd024f81615176897; _ga=GA1.2.1513737719.1615176899; _gid=GA1.2.1327041807.1615176899; hubspotutk=0e00e2625f2068d6a36e915cd36c7b59; __hssrc=1; __hs_opt_out=no; __hs_initial_opt_in=true; PHPSESSID=i3i8bit64m9f4gtilt5qfpthmh; __hstc=6077420.0e00e2625f2068d6a36e915cd36c7b59.1615177010946.1615177010946.1615181523479.2; _gat=1; __hssc=6077420.5.1615181523479",
                # "cookie": "__cfduid=d6d00b7e7c3e594db5594b2c4cdd024f81615176897; _ga=GA1.2.1513737719.1615176899; _gid=GA1.2.1327041807.1615176899; __hstc=6077420.0e00e2625f2068d6a36e915cd36c7b59.1615177010946.1615177010946.1615177010946.1; hubspotutk=0e00e2625f2068d6a36e915cd36c7b59; __hssrc=1; __hssc=6077420.1.1615177010947; __hs_opt_out=no; __hs_initial_opt_in=true",
                "origin": "https://ark-funds.com",
                "pragma": "no-cache",
                "referer": "https://ark-funds.com/arkk",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
                "x-requested-with": "XMLHttpRequest", }

    def get_content(self, fund_name):
        post_data = self.data.copy()
        post_data['ticker'] = fund_name

        content = self.post(url=self.url, post_data=post_data)
        # print('content')
        # print(content)
        return content

    def parse(self, content,types):
        response = Selector(text=content)
        table = response.xpath('//table[@id="top10h"]/tr')
        holding_list = []
        date = response.xpath(
            '//div[@class="asofdate floatleft"]/text()').extract_first()
        try:
            date = date.replace('As of ', '')
            date = datetime.datetime.strptime(date,'%m/%d/%Y').strftime('%Y-%m-%d')
        except Exception as e:
            print(e)
            t=response.xpath(
            '//div[@class="asofdate floatleft"]/text()').extract_first()
            print(t)
        for item in table[1:]:
            item_dict = {}
            percent = item.xpath('.//td[1]/text()').extract_first()
            name = item.xpath('.//td[2]/text()').extract_first()
            short_name = item.xpath('.//td[3]/text()').extract_first()
            price = item.xpath('.//td[4]/text()').extract_first()
            share_hold = item.xpath('.//td[5]/text()').extract_first()
            market_value = item.xpath('.//td[6]/text()').extract_first()
            item_dict['holding_percent'] = percent
            item_dict['name'] = name
            item_dict['short_name'] = short_name
            item_dict['price'] = price
            item_dict['share_hold'] = share_hold
            item_dict['market_value'] = market_value
            item_dict['date']=date
            item_dict['type']=types
            holding_list.append(item_dict)

        return holding_list

    
    def save_data(self,date_list):
        count=0
        while count<MAX_COUNT:
            try:
                self.doc.insert_many(date_list)
            except Exception as e:
                self.logger.error(e)
                count+=1
            else:
                return True
        return False
    def get_fund_holding(self,fund_name = 'ARKK'):
                
        content = self.get_content(fund_name)
        holding_list = self.parse(content,fund_name)
        # print(holding_list)
        if not self.save_data(holding_list):
            self.notify('ark save mongo failed')

    def start(self):
        fund_list=['arkk','arkq','arkw','arkg','arkf']
        for fund in fund_list:
            self.get_fund_holding(fund.upper())


if __name__ == '__main__':
    app = ARKFundSpider()
    app.start()
