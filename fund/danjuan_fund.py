import datetime
import sys
import time
from typing import Deque

sys.path.append('..')
from common.BaseService import BaseService
from configure.settings import DBSelector


class Danjuan(BaseService):

    def __init__(self) -> None:
        super(Danjuan, self).__init__('../log/danjuan.log')
        self.base_url = 'https://danjuanfunds.com/djapi/fundx/portfolio/v3/plan/united/page?tab=4&page={}&size=20&default_order=0&invest_strategy=&type=&manager_type=&yield_between=&mz_between='
        self.detail_url = 'https://danjuanfunds.com/djapi/plan/position/detail?plan_code={}'
        self.plan_detail_url = 'https://danjuanfunds.com/djapi/plan/{}'

        self.__headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7",
            "Host": "danjuanfunds.com",
            "Referer": "https://danjuanfunds.com/activity/GroupBigV",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
        }

        self.db = DBSelector().mongo(location_type='qq')
        date=datetime.datetime.now().strftime("%Y-%m-%d")
        self.main_doc = self.db['db_danjuan'][f'danjuan_fund_{date}']
        self.mongo_init()

    def mongo_init(self):
        try:
            self.main_doc.ensure_index('plan_code', unique=True)
        except Exception as e:
            self.logger.error(e)

    @property
    def headers(self):
        return self.__headers

    def crawl(self, page):
        # page = 1
        full_url = self.base_url.format(page)
        content = self.get(url=full_url, _json=True
                           )
        return content

    def parse(self, content):
        return content.get('data', {}).get('items', [])

    def save_data(self, data_list):
        for item in data_list:
            try:
                self.main_doc.insert_one(item)
            except Exception as e:
                self.logger.error(e)


    def get_plan_code(self):
        MAX_PAGE = 50
        for page in range(1, MAX_PAGE): # 暂定 50页，实际数据很少
            content = self.crawl(page)
            return_data = self.parse(content)
            self.save_data(return_data)
            time.sleep(1)


    @property
    def code_list(self):
        return self.main_doc.find({}, {'plan_code': 1})

    def update_data(self, condition, data):

        try:
            self.main_doc.update_one(condition, {'$set': data})
        except Exception as e:
            self.logger.error(e)
        else:
            print('update passed!')

    def plan_detail(self):

        for code in self.code_list:
            code = code.get('plan_code')
            url = self.plan_detail_url.format(code)
            content = self.get(url=url, _json=True)
            if content.get('data'):
                detail_info = content.get('data')
                detail_info = self.post_process(detail_info)
                self.update_data({'plan_code': code}, detail_info)
            else:
                self.logger.error('code {} is empty'.format(code))

    def post_process(self, detail_info):
        '''
        移除无用字段
        '''
        keys = ['plan_name',
                'plan_code',
                'yield',
                'type',
              'yield_name',

                ]
        for key in keys:
            del detail_info[key]

        return detail_info

    def get_holding_fund_detail(self):
        '''
        持仓详情
        '''
        for code in self.code_list:
            code = code.get('plan_code')
            url = self.detail_url.format(code)
            content = self.get(url=url, _json=True)
            if content.get('data'):
                holdings = content.get('data').get('items')
                
                self.update_data({'plan_code': code}, {"holding": holdings})
            else:
                self.logger.error('code {} is empty'.format(code))

    def run(self):
        self.get_plan_code() # 获取plan code 并入库
        self.get_holding_fund_detail() # 获取具体持仓
        self.plan_detail()  # 方案的持有信息，收益等


if __name__ == '__main__':
    app = Danjuan()
    app.run()
