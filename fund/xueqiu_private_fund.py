import datetime
import sys
import re
import requests
sys.path.append('..')
from configure.settings import DBSelector, config
from common.BaseService import BaseService
from parsel import Selector


# 雪球私募数据获取
# 需要用cookies

class PrivateFund(BaseService):

    def __init__(self):
        super(PrivateFund, self).__init__('../log/privatefund.log')
        self.db = None
        self.init_db()
        self.today_str = datetime.date.today().strftime("%Y-%m-%d")
        self.doc = self.db['xueqiu_private_{}'.format(self.today_str)]
        self.logger.info("========")

    def get_cookies(self):
        return config.get("xueqiu_cookies", "")  # 在configure文件夹中的config.json 加入 “xueqiu_cookies”:"xxxxxxxxxxxxxx"

    @property
    def headers(self):

        return {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7",
            "Host": "xueqiu.com",
            "Cookie": self.get_cookies(),
            "Pragma": "no-cache",
            "Referer": "https://xueqiu.com/f/rank",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }

    def update_with_missing_data(self):
        # 按默认列表排序，失去部分数据，使用不同条件合并数据
        order_option = ['PROFIT', 'DRAWDOWN', 'SHARP']
        url = "https://xueqiu.com/private_fund/v3/rank/list.json?order_by={}&typical=&strategy=&fund_type=&period=all&annual_period=0&launch_date=&max_drawdown_range=0&match_risk=false&fund_status="
        for option in order_option:
            url_ = url.format(option)
            content = self.get(url=url_, _json=True)
            data = self.parse(content)
            self.update_db(data)

    def update_db(self, data):

        for item in data:
            if self.isExist(item['symbol']):
                continue
            self.doc.insert_one(item)

    def isExist(self, code):
        return True if self.doc.find_one({'symbol': code}) else False

    def run(self):
        import warnings
        warnings.warn("using update_with_missing_data function")
        # 不需要登录即可拿到数据, 复制cookies数据 单个数据
        url = "https://xueqiu.com/private_fund/v3/rank/list.json?order_by=PROFIT&typical=&strategy=&fund_type=&period=all&annual_period=0&launch_date=&max_drawdown_range=0&match_risk=false&fund_status="
        content = self.get(url=url, _json=True)
        data = self.parse(content)
        self.store_db(data)

    def init_db(self):
        self.db = DBSelector().mongo('qq')['db_stock']

    def parse(self, content):
        data = content['data'] or []
        for item in data:
            item['crawltime'] = datetime.datetime.now()
        return data

    def store_db(self, data):
        self.doc.insert_many(data)

    def debug(self):
        # result=doc.find_one()
        result = self.doc.find_one(
            {'crawltime': {'$gt': datetime.datetime.strptime('2021-12-26 13:00:00', "%Y-%m-%d %H:%M:%S")}})
        # print(result)

    def get_details(self):
        for code in self.get_all_code():
            self.get_detail(code)

    def get_detail(self, code):
        # 获取日期
        url = "https://xueqiu.com/S/{}"

        content = self.get(url=url.format(code))
        create_date, publish_date = self.parse_detail(content)
        print(create_date, publish_date)
        self.update_create_publish_date(code, create_date, publish_date)

    def update_create_publish_date(self, code, create_date, publish_date):

        self.doc.update_one({'symbol': code}, {"$set": {"create_date": create_date, "netvalue_date": publish_date}})

    def parse_detail(self, content):
        # print(content)
        resp = Selector(text=content)
        date = resp.xpath('//span[@class="date"]/text()').extract_first()
        publish_date = resp.xpath('//div[@class="values-date period"]/text()').extract_first()
        # "values-date period"
        # print(date)
        match = re.search("（ 成立于 (.*?) ）", date)
        if match:
            create_date = match.group(1)
        else:
            create_date = None

        netvalue_date_match = re.search(" 净值日期：(.*)", publish_date)
        if netvalue_date_match:
            publish_date = netvalue_date_match.group(1)
        else:
            publish_date = None

        return create_date, publish_date

    def isCrawl(self, symbol):
        if self.db['xueqiu_private_process_{}'.format(self.today_str)].find_one({'symbol': symbol}):
            return True
        else:
            return False

    def checkValid(self, content):
        return False if re.search("服务器出错了", content) else True
    def get_(self, url, _json=False, binary=False, retry=5):

        cookies = {
            'device_id': '30c150d8bba6b59a776c2e783ab3baf4',
            's': 'by1hv4ciih',
            '__utmz': '1.1645204918.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
            'bid': 'a8ec0ec01035c8be5606c595aed718d4_kztd4jue',
            'xq_is_login': '1',
            'u': '1733473480',
            'xq_a_token': 'b5d4b0bb48c361274af3657413be877434c6b846',
            'xqat': 'b5d4b0bb48c361274af3657413be877434c6b846',
            'xq_id_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjE3MzM0NzM0ODAsImlzcyI6InVjIiwiZXhwIjoxNjYyMzU3NTczLCJjdG0iOjE2NTk3NjU1NzM3NDgsImNpZCI6ImQ5ZDBuNEFadXAifQ.FYBLTo0xn2AftqnYRhqrpEk6a_09l4vZVQS4k5f4k7rbIYSVAYCULq-WvsifcjiRYalF7C2Dje8_JnoI3fg7C0EuvLOh1DmqfDUSmnSUj3SbGW_Ht1X8q656BZrCE7fqIeNgEmMO8cO1IwW64kU_821jIgWfVUl62Nb9uSzlI_RzpH5DjM1D6XVvV0W-iH9JqddgPHLc4NykMF5AO_q_vqmeQe2k-wC2hUbryBtZiSyx187E0YLUVulkMKXScvODFeYzSkZ7sPW4idfA4dlrVhD5rY2J8drSJGnOif5siDsEHFMCloXrORaHysSys-pdvoxJVuV3aUzpunpf9fuGIg',
            'xq_r_token': 'de0c71fb63884746aabd6a37fe13a40ce56196cc',
            '__utma': '1.1751771128.1645204918.1659977612.1660301449.14',
            'acw_tc': '2760825c16607935161586753e9c4bcdd770c342a15d6a1e565c8bc39f2ab4',
            'Hm_lvt_1db88642e346389874251b5a1eded6e3': '1660708494,1660727447,1660735985,1660793521',
            'Hm_lvt_fe218c11eab60b6ab1b6f84fb38bcc4a': '1659978973,1660318981,1660793586',
            'Hm_lpvt_1db88642e346389874251b5a1eded6e3': '1660793631',
            'Hm_lpvt_fe218c11eab60b6ab1b6f84fb38bcc4a': '1660794474',
        }

        headers = {
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6',
            # Requests sorts cookies= alphabetically
            # 'Cookie': 'device_id=30c150d8bba6b59a776c2e783ab3baf4; s=by1hv4ciih; __utmz=1.1645204918.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); bid=a8ec0ec01035c8be5606c595aed718d4_kztd4jue; xq_is_login=1; u=1733473480; xq_a_token=b5d4b0bb48c361274af3657413be877434c6b846; xqat=b5d4b0bb48c361274af3657413be877434c6b846; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOjE3MzM0NzM0ODAsImlzcyI6InVjIiwiZXhwIjoxNjYyMzU3NTczLCJjdG0iOjE2NTk3NjU1NzM3NDgsImNpZCI6ImQ5ZDBuNEFadXAifQ.FYBLTo0xn2AftqnYRhqrpEk6a_09l4vZVQS4k5f4k7rbIYSVAYCULq-WvsifcjiRYalF7C2Dje8_JnoI3fg7C0EuvLOh1DmqfDUSmnSUj3SbGW_Ht1X8q656BZrCE7fqIeNgEmMO8cO1IwW64kU_821jIgWfVUl62Nb9uSzlI_RzpH5DjM1D6XVvV0W-iH9JqddgPHLc4NykMF5AO_q_vqmeQe2k-wC2hUbryBtZiSyx187E0YLUVulkMKXScvODFeYzSkZ7sPW4idfA4dlrVhD5rY2J8drSJGnOif5siDsEHFMCloXrORaHysSys-pdvoxJVuV3aUzpunpf9fuGIg; xq_r_token=de0c71fb63884746aabd6a37fe13a40ce56196cc; __utma=1.1751771128.1645204918.1659977612.1660301449.14; acw_tc=2760825c16607935161586753e9c4bcdd770c342a15d6a1e565c8bc39f2ab4; Hm_lvt_1db88642e346389874251b5a1eded6e3=1660708494,1660727447,1660735985,1660793521; Hm_lvt_fe218c11eab60b6ab1b6f84fb38bcc4a=1659978973,1660318981,1660793586; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1660793631; Hm_lpvt_fe218c11eab60b6ab1b6f84fb38bcc4a=1660794474',
        }

        response = requests.get(url,
                                cookies=cookies,
                                headers=headers)
        return response.text

    def fund(self, symbol):
        url = "https://xueqiu.com/S/{}"
        if self.isCrawl(symbol):
            return ""

        content = self.get(url=url.format(symbol))
        if not self.checkValid(content):
            print('no valid')
            self.db['xueqiu_private_process_{}'.format(self.today_str)].update_one({'symbol': symbol},
                                                         {"$set": {"symbol": symbol, 'status': 0}},
                                                         True, True)
            return ""

        item = self.parse_detect(symbol, content)
        if item is None:
            return ""

        if item['name']  is None:
            self.db['xueqiu_private_process_{}'.format(self.today_str)].update_one({'symbol': symbol},
                                                         {"$set": {"symbol": symbol, 'status': 1}},
                                                         True, True)
            return ""

        try:
            self.doc.insert_one(item)
        except Exception as e:
            self.logger.error(e)
            return "{} error".format(symbol)
        else:
            self.db['xueqiu_private_process_{}'.format(self.today_str)].update_one({'symbol': symbol},
                                                         {"$set": {"symbol": symbol, 'status': 1}},
                                                         True, True)
            return symbol

    def parse_detect(self, symbol, content):
        return_item = {}
        resp = Selector(text=content)

        name = resp.xpath('//div[@class="cube-title"]/span[@class="name"]/text()').extract_first()
        profit_rate = resp.xpath('//div[@class="cube-profit-year fn-clear"]/span[@class="per"]/text()').extract_first()
        annual_return_this_year = resp.xpath(
            '//div[@class="cube-profits fn-clear"]/div[@class="cube-profit-day cube-profit"][4]/div[2]/text()').extract_first()
        manager_nick_name = resp.xpath('//div[@class="name fn-clear"]/span/text()').extract_first()

        create_date = resp.xpath('//span[@class="date"]/text()').extract_first()
        publish_date = resp.xpath('//div[@class="values-date period"]/text()').extract_first()

        if create_date is None:
            create_date = None
        else:
            match = re.search("（ 成立于 (.*?) ）", create_date)

            if match:
                create_date = match.group(1)
            else:
                create_date = None

        if publish_date is None:
            publish_date = None
        else:
            netvalue_date_match = re.search(" 净值日期：(.*)", publish_date)

            if netvalue_date_match:
                publish_date = netvalue_date_match.group(1)
            else:
                publish_date = None

        try:
            profit_rate = float(profit_rate)
        except:
            profit_rate = None

        try:
            annual_return_this_year = annual_return_this_year.replace("%", "")
            annual_return_this_year = float(annual_return_this_year)
        except:
            annual_return_this_year = None
        close_status = False
        if 'https://assets.imedao.com/images/cube-closed.png' in content:
            close_status = True

        return_item['symbol'] = symbol
        return_item['name'] = name
        return_item['profit_rate'] = profit_rate
        return_item['annual_return_this_year'] = annual_return_this_year
        return_item['manager_nick_name'] = manager_nick_name
        return_item['netvalue_date'] = publish_date
        return_item['create_date'] = create_date
        return_item['close_status'] = close_status
        return_item['crwaltime'] = datetime.datetime.now()

        return return_item

    def get_all_code(self):
        codes = []
        for item in self.doc.find({}, {"symbol": 1}):
            codes.append(item['symbol'])
        return codes

    def generate_code(self):
        start = 0
        end = 1500
        code_list = []
        for i in range(start, end):
            symbol = "P" + str(i).zfill(6)
            code_list.append(symbol)
        return code_list

    def brute_force(self):
        from concurrent.futures import ThreadPoolExecutor, as_completed
        executor = ThreadPoolExecutor(max_workers=5)
        code_list = self.generate_code()
        thread_list = [executor.submit(self.fund, (code,)) for code in code_list]
        for future in as_completed(thread_list):
            data = future.result()
            print("{} Done".format(data))

    def seq_run(self):
        code_list = self.generate_code()
        for code in code_list:
            self.fund(code)

    def update_nick_name(self):
        need_to_be_updated = self.db['xueqiu_private_2021-12-28_brute_force'].find({'manager_nick_name':None},{'_id':1,'symbol':1})
        for item in need_to_be_updated:
            # print(item)
            s_fund = self.doc.find_one({'symbol':item['symbol']})
            if s_fund is None:
                continue

            print('update ',s_fund['manager_nick_name'])
            self.db['xueqiu_private_2021-12-28_brute_force'].update_one({"_id":item['_id']},{"$set":{'manager_nick_name':s_fund['manager_nick_name']}})

            

def main():
    app = PrivateFund()
    # app.run()
    app.update_with_missing_data()
    # app.debug()
    # app.get_details()
    # app.brute_force()
    # app.fund('P000946')
    # app.seq_run()
    # app.update_nick_name()

if __name__ == '__main__':
    main()
