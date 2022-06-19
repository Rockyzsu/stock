import time
import datetime
import fire
import requests
import sys
sys.path.append('..')

from configure.settings import DBSelector
from configure.util import js2json

# code = '270042'
# name = '广发纳指100ETF联接人民币(QDII)C'
# year = '2016'


headers = {
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6",
    "Cookie": "qgqp_b_id=332e88303d7106e94890d3f5092fefe0; em_hq_fls=js; HAList=a-sz-300636-%u540C%u548C%u836F%u4E1A%2Cty-107-XOP-%u6CB9%u6C14%u5F00%u91C7ETF-SPDR%20S%26P%2Cty-105-SQQQ-%u4E09%u500D%u505A%u7A7A%u7EB3%u65AF%u8FBE%u514B100ETF%2Ca-sh-603876-%u9F0E%u80DC%u65B0%u6750%2Ca-sz-000599-%u9752%u5C9B%u53CC%u661F%2Cty-1-113534-%u9F0E%u80DC%u8F6C%u503A%2Cty-0-160143-%u521B%u4E1A%u677F%u5B9A%u5F00%u5357%u65B9%2Ca-sz-002455-%u767E%u5DDD%u80A1%u4EFD%2Cty-116-00700-%u817E%u8BAF%u63A7%u80A1; em-quote-version=topspeed; st_si=77333725236219; st_asi=delete; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; ASP.NET_SessionId=yionbf3rvyddx1kplfv4jo3a; EMFUND0=null; EMFUND7=06-06%2018%3A11%3A09@%23%24%u5E7F%u53D1%u7EB3%u65AF%u8FBE%u514B100ETF@%23%24159941; EMFUND8=06-06%2018%3A14%3A07@%23%24%u5E7F%u53D1%u7EB3%u6307100ETF%u8054%u63A5%u4EBA%u6C11%u5E01%28QDII%29C@%23%24006479; EMFUND9=06-06%2018%3A23%3A04@%23%24%u5E7F%u53D1%u7EB3%u6307100ETF%u8054%u63A5%u4EBA%u6C11%u5E01%28QDII%29A@%23%24270042; EMFUND6=06-06 18:23:27@#$%u56FD%u6CF0%u7EB3%u65AF%u8FBE%u514B100ETF@%23%24513100; st_pvi=30849193689390; st_sp=2022-02-19%2022%3A30%3A59; st_inirUrl=https%3A%2F%2Ffund.eastmoney.com%2F; st_sn=21; st_psi=20220606182327258-112200305282-6535572517",
    "Host": "fundf10.eastmoney.com",
    "Referer": "http://fundf10.eastmoney.com/ccmx_159941.html",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
}



class FundHolding():

    def __init__(self, code, year,is_stock=True) -> None:
        self.current_year = year
        self.code = code
        client = DBSelector().mongo('qq')
        self.doc = client['db_stock']['fund_component_{}'.format(code)]
        self.is_stock= is_stock # 股还是债
    
    @property
    def FLAG(self):
        return '股' if self.is_stock else '债'

    def get_content(self, code, year):
        print('year ========== ', year)
        if self.is_stock:
            url = 'http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=jjcc&code={}&topline=10&year={}&month=&rt=0.7286081766586014'.format(
            code, year)
        else:
            url = 'http://fundf10.eastmoney.com/FundArchivesDatas.aspx?type=zqcc&code={}&topline=10&year={}&month=&rt=0.7286081766586014'.format(
            code, year)

        resp = requests.get(url,
                            headers=headers)
        data = js2json(resp.text)
        return data['content'], data['arryear']

    def insert_mongodb(self, item):
        try:
            self.doc.update_one({'name':item['name'],'date':item['date']},{'$set':item},upsert=True)
        except Exception as e:
            print(e)

    def parse(self, content):
        from parsel import Selector
        resp = Selector(text=content)
        boxes = resp.xpath('//div[@class="box"]')

        for box in boxes:
            date = box.xpath(
                './/div[@class="boxitem w790"]/h4/label[@class="right lab2 xq505"]/font/text()').extract_first()
            rows = box.xpath(
                './/div[@class="boxitem w790"]/table[@class="w782 comm tzxq t2"]/tbody/tr')
            if len(rows) == 0:
                rows = box.xpath(
                    './/div[@class="boxitem w790"]/table[@class="w782 comm tzxq"]/tbody/tr')

            for _row in rows:
                item = {}
                row = _row.xpath('.//td')
                if len(row) == 9:
                    name = row[1].xpath('.//a/text()').extract_first()
                    chn_name = row[2].xpath('.//a/text()').extract_first()
                    weight = row[6].xpath('.//text()').extract_first()
                    holding_share = row[7].xpath('.//text()').extract_first()
                    holding_mount = row[8].xpath('.//text()').extract_first()
                else:
                    if self.is_stock:
                        name = row[1].xpath('.//a/text()').extract_first()
                        chn_name = row[2].xpath('.//a/text()').extract_first()
                        weight = row[4].xpath('.//text()').extract_first()
                        holding_share = row[5].xpath('.//text()').extract_first()
                        holding_mount = row[6].xpath('.//text()').extract_first()

                    else:
                        # 债
                        if len(row)==5:
                            name = row[1].xpath('.//text()').extract_first()
                            chn_name = row[2].xpath('.//text()').extract_first()
                            weight = row[3].xpath('.//text()').extract_first()
                            holding_mount = row[4].xpath('.//text()').extract_first()
                            holding_share=None

                item['name'] = name
                item['chn_name'] = chn_name
                item['weight'] = weight
                item['holding_mount'] = holding_mount
                item['holding_share'] = holding_share
                item['date'] = date
                item['type']=self.FLAG
                item['crawltime'] = datetime.datetime.now()
                self.insert_mongodb(item)

            print('====')

    def run(self):

        _, years = self.get_content(self.code, self.current_year)

        for year in years:
            content, _year = self.get_content(self.code, year)
            self.parse(content)
            time.sleep(3)


def main(year='2022', code='008331',is_stock=False):
    app = FundHolding(code, year,is_stock)
    app.run()

def paralle_run():
    code_list = [{'code': '008331', 'name': '万家可转债债券A'}, {'code': '000297', 'name': '鹏华可转债'},
                 {'code': '006482', 'name': '广发可转债债券A'}, {'code': '000536', 'name': '前海开源可转债债券'},
                 {'code': '310518', 'name': '申万菱信可转债债券A'}, {'code': '240018', 'name': '华宝可转债债券'},
                 {'code': '340001', 'name': '兴全可转债混合'}, {'code': '005273', 'name': '华商可转债A'},
                 {'code': '470058', 'name': '汇添富可转换债券A'}, {'code': '110035', 'name': '易方达双债增强A'},
                 {'code': '008809', 'name': '安信民稳增长混合A'}, {'code': '005876', 'name': '易方达鑫转增利混合A'},
                 {'code': '006102', 'name': '浙商丰利增强债券'}, {'code': '003092', 'name': '华商丰利增强定开债A'}]

    for code in code_list:
        code_=code['code']
        name=code['name']
        app = FundHolding(code_,'2022',False)
        app.run()

if __name__ == '__main__':
    # fire.Fire(main)
    paralle_run()