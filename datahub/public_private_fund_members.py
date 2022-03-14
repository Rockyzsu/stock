# 公募私募人员数据获取
import math
import sys

sys.path.append('..')
from configure.settings import DBSelector
from common.BaseService import BaseService
import requests
import warnings
import datetime
warnings.filterwarnings("ignore")



class FundMembers(BaseService):

    def __init__(self, kind, date, first_use=False):
        super(FundMembers, self).__init__(first_use)

        self.lof_url = 'http://query.sse.com.cn/commonQuery.do?=&jsonCallBack=jsonpCallback1681&sqlId=COMMON_SSE_FUND_LOF_SCALE_CX_S&pageHelp.pageSize=10000&FILEDATE={}&_=161146986468'
        self.etf_url = 'http://query.sse.com.cn/commonQuery.do?jsonCallBack=jsonpCallback28550&isPagination=true&pageHelp.pageSize=25&pageHelp.pageNo={}&pageHelp.cacheSize=1&sqlId=COMMON_SSE_ZQPZ_ETFZL_XXPL_ETFGM_SEARCH_L&STAT_DATE={}&pageHelp.beginPage={}&pageHelp.endPage=30&_=1611473902414'

        self.db = DBSelector()

        # self.today ='2021-01-22' # ETF
        self.today_='' # TODO failed
        self.ETF_COUNT_PER_PAGE = 25
        self.url_option_dict = {
            'ETF': {'url': self.etf_url, 'date': self.today},
            'LOF': {'url': self.lof_url, 'date': self.today_}
        }

        self.kind = kind.lower()
        self.session = requests.Session()
        self.logger.info('start...sh fund')
        self.LAST_TEXT = ''

        if first_use:
            self.create_table()

        self.db_session = self.get_session()
        self.sess = self.db_session()

    def crawl_lof(self):
        options = self.url_option_dict['LOF']
        date = options.get('date')
        url = options.get('url')
        content = self.get(url.format(date), js=False)
        js_data = self.jsonp2json(content)
        self.process_lof(js_data)

    @property
    def headers(self):
        return {
            "Host": "query.sse.com.cn",
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Referer": "http://www.sse.com.cn/market/funddata/volumn/lofvolumn/",
        }

    def process_lof(self, js_data):
        result = js_data.get('result')
        for item in result:
            code = item['FUND_CODE']
            name = item['FUND_ABBR']
            date = item['TRADE_DATE']

            try:
                share = float(item['INTERNAL_VOL'].replace(',', ''))
            except Exception as e:
                print(e)
                share = None

            self.process_model(code, name, date, share, 'LOF')

    def post(self, url, post_data, _josn=False, binary=False, retry=5):
        pass

    def crawl_etf(self):
        options = self.url_option_dict['ETF']
        date = options.get('date')
        url = options.get('url')
        current_page = 1
        while True:
            content = self.get(url.format(current_page, date, current_page), _json=False)
            js_data = self.jsonp2json(content)
            total_count = js_data.get('pageHelp').get('total')
            print(f'page : {current_page}')
            self.process_etf(js_data)

            max_page = math.ceil(total_count / self.ETF_COUNT_PER_PAGE)  # 每页 10个

            if current_page > max_page:
                break

            current_page += 1

    def process_etf(self, js_data):
        result = js_data.get('result')
        for item in result:
            code = item['SEC_CODE']
            name = item['SEC_NAME']
            date = item['STAT_DATE']
            share = item['TOT_VOL']
            try:
                share = float(share)
            except Exception as e:
                print(e)

            self.process_model(code, name, date, share, 'ETF')

    def run(self):
        'LOF 与 ETF'
        # for type_, options in self.url_option_dict.items():
        if self.kind == 'etf':
            self.logger.info('crawling etf .....')
            self.crawl_etf()
        if self.kind == 'lof':
            self.logger.info('crawling lof .....')
            self.crawl_lof()

    def process_model(self, code, name, date, share, type_):
        obj = self.sess.query(FundBaseInfoModel).filter_by(code=code).first()
        if not obj:
            obj = FundBaseInfoModel(
                code=code,
                name=name,
                category=type_,
                invest_type=None,
                manager_name=None,
                issue_date=None,
            )
            try:
                self.sess.add(obj)
            except Exception as e:
                print(e)
            else:
                self.sess.commit()
                print(f'插入一条记录{code}，{date}')

        if not self.sess.query(ShareModel).filter_by(code=code, date=date).first():

            share_info = ShareModel(
                code=code,
                date=date,
                share=share,
                crawltime=datetime.datetime.now(),
            )
            try:
                self.sess.add(share_info)
            except Exception as e:
                print(e)
            else:
                print(f'插入一条记录{code}，{date}')
                self.sess.commit()
