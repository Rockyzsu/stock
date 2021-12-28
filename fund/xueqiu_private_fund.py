import datetime
import sys

sys.path.append('..')
from configure.settings import DBSelector
from common.BaseService import BaseService


# 雪球私募数据获取

class PrivateFund(BaseService):

    def __init__(self):
        super(PrivateFund, self).__init__('../log/privatefund.log')
        self.db = None
        self.init_db()

    @property
    def headers(self):
        return {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7",
            "Host": "xueqiu.com",
            "Pragma": "no-cache",
            "Referer": "https://xueqiu.com/f/rank",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }

    def run(self):
        # 不需要登录即可拿到数据
        url = "https://xueqiu.com/private_fund/v3/rank/list.json?order_by=PROFIT&typical=&strategy=&fund_type=&period=all&annual_period=0&launch_date=&max_drawdown_range=0&match_risk=false&fund_status="
        content=self.get(url=url,_json=True)
        data = self.parse(content)
        self.store_db(data)

    def init_db(self):
        self.db = DBSelector().mongo('qq')['db_stock']

    def parse(self, content):
        data= content['data'] or []
        for item in data:
            item['crwaltime']=datetime.datetime.now()
        return data

    def store_db(self,data):
        today_str = datetime.date.today().strftime("%Y-%m-%d")

        doc = self.db['xueqiu_private_{}'.format(today_str)]
        doc.insert_many(data)

def main():
    app = PrivateFund()
    app.run()

if __name__ == '__main__':
    main()