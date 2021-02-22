# -*- coding: utf-8 -*-
# website: http://30daydo.com
# @Time : 2020/2/20 17:06
# @File : etf_info.py
# 获取etf的成分股数据

# 重构 2021-01-21

import datetime
import pymongo
import re
import requests
import sys
from parsel.selector import Selector
from sqlalchemy.orm import sessionmaker
from loguru import logger
sys.path.append('..')

from common.BaseService import BaseService
from configure.settings import DBSelector
from fund.etf_models import IndexObject, IndexObjectNew, Base

TIMEOUT = 30 # 超时


class Fund(BaseService):

    def __init__(self, first_use=False):
        super(Fund, self).__init__(f'../log/{self.__class__.__name__}.log')
        self.first_use = first_use
        self.engine = self.get_engine()

    def get_engine(self):
        return DBSelector().get_engine('db_stock')

    def create_table(self):
        # 初始化数据库连接:
        Base.metadata.create_all(self.engine)  # 创建表结构

    def get_session(self):
        return sessionmaker(bind=self.engine)

    def get(self, url, retry=5, js=True):
        start = 0
        while start < retry:
            try:
                response = self.session.get(url, headers=self.headers,
                                            verify=False)
            except Exception as e:
                self.logger.error(e)
                start += 1

            else:
                if js:
                    content = response.json()
                else:
                    content = response.text

                return content

        if start == retry:
            self.logger.error('重试太多')
            return None


class IndexSpider(Fund):

    def __init__(self, first_use=False):
        super(IndexSpider, self).__init__(first_use)

        if first_use:
            self.create_table()

        self.sess = self.get_session()()
        self.base_url = 'http://www.csindex.com.cn/zh-CN/indices/index-detail/{}'
        self.download_url = 'http://www.csindex.com.cn/uploads/file/autofile/cons/{}cons.xls'

    def basic_info(self):

        '''
        基本数据，没有仓位的
        拿到的只是上证的数据, ??? 中证吧
        :return:
        '''

        r = requests.get(url='http://www.csindex.com.cn/zh-CN/search/indices?about=1',
                         headers={'User-Agent': 'Molliza Firefox Chrome'})

        response = Selector(text=r.text)
        table = response.xpath('//table[@class="table table-even table-bg  tc p_table tablePage"]')
        index_list = table[0].xpath('.//tbody[@id="itemContainer"]/tr')

        for idx in index_list:
            code = idx.xpath('.//td[1]/a/text()').extract_first()
            detail_url = idx.xpath('.//td[1]/a/@href').extract_first()
            name = idx.xpath('.//td[2]/a/text()').extract_first()
            stock_count = idx.xpath('.//td[3]/text()').extract_first()
            price = idx.xpath('.//td[4]/text()').extract_first()
            month_ratio = idx.xpath('.//td[5]/text()').extract_first()
            month_ratio = month_ratio.replace('--', '')
            if len(month_ratio) == 0:
                month_ratio = 0

            type_ = idx.xpath('.//td[6]/text()').extract_first()
            hot_pot = idx.xpath('.//td[7]/text()').extract_first()
            area = idx.xpath('.//td[8]/text()').extract_first()
            coin = idx.xpath('.//td[9]/text()').extract_first()
            specified = idx.xpath('.//td[10]/text()').extract_first()
            index_type = idx.xpath('.//td[11]/text()').extract_first()

            obj = IndexObject(
                代码=code,
                详细URL=detail_url,
                指数名称=name,
                股票数目=stock_count,
                最新收盘=float(price),
                一个月收益率=float(month_ratio),
                资产类别=type_,
                热点=hot_pot,
                地区覆盖=area,
                币种=coin,
                定制=specified,
                指数类别=index_type
            )

            try:
                self.sess.add(obj)
            except Exception as e:
                logger.error(e)
                self.sess.rollback()
            else:
                self.sess.commit()

    def etf_detail_with_product_inuse(self):
        '''
        获取到所有的成分，不过没有权重
        :return:
        '''
        self.client = DBSelector().mongo()
        self.db = self.client['fund']
        # self.doc = client['fund']['etf_info']

        ret = self.sess.query(IndexObjectNew).all()
        sess = requests.Session()

        for i in ret:
            code = i.代码
            name = i.指数名称
            self.etf_detail_constituent_stock(sess, code, name)

    def full_market(self):
        '''
        勾选了 中证，上证，深证
        :return:
        '''
        total = 1797  # hard code
        page_size = 50
        total_page = total // page_size + 1

        url = 'http://www.csindex.com.cn/zh-CN/indices/index?page={}&page_size=50&by=asc&order=%E5%8F%91%E5%B8%83%E6%97%B6%E9%97%B4&data_type=json&class_1=1&class_2=2&class_3=3'
        for i in range(1, total_page + 1):
            r = requests.get(url.format(i), headers={'User-Agent': 'Molliza Firefox Chrome'})
            ret = r.json()

            for item in ret.get('list'):

                index_id = item.get('index_id')
                index_code = item.get('index_code')
                index_sname = item.get('indx_sname')
                index_ename = item.get('index_ename')
                num = item.get('num')
                tclose = item.get('tclose')
                yld_1_mon = item.get('yld_1_mon')
                base_point = item.get('base_point')
                index_c_intro = item.get('index_c_intro')
                index_c_fullname = item.get('index_c_fullname')
                class_assets = item.get('class_assets')
                class_series = item.get('class_series')
                class_classify = item.get('class_classify')
                class_hot = item.get('class_hot')
                class_region = item.get('class_region')

                obj = IndexObjectNew(
                    # id=index_id,
                    代码=index_code,
                    指数名称=index_sname,
                    指数英文名称=index_ename,
                    股票数目=num,
                    最新收盘=tclose,
                    一个月收益率=yld_1_mon,
                    基准点数=base_point,
                    指数介绍=index_c_intro,
                    指数全称=index_c_fullname,
                    资产类别=class_assets,
                    指数系列=class_series,
                    热点=class_hot,
                    地区覆盖=class_region,
                    指数类别=class_classify,
                    获取时间=datetime.datetime.now()
                )

                try:
                    self.sess.add(obj)
                except Exception as e:
                    logger.error(e)
                    self.sess.rollback()

                else:
                    self.sess.commit()

    def download_excel_file(self, sess, code, name):
        s = sess.get(self.download_url.format(code), headers={'User-Agent': 'Molliza Firefox Chrome'},timeout=TIMEOUT)
        with open('../data/etf/{}_{}.xls'.format(code, name), 'wb') as f:
            f.write(s.content)

    def get_qz_page(self, sess, code):
        '''
        获取权重页面
        :return:
        '''
        # 获取权重
        qz_url = 'http://www.csindex.com.cn/zh-CN/indices/index-detail/{}'
        s1 = sess.get(qz_url.format(code), headers={'User-Agent': 'Molliza Firefox Chrome'})
        return Selector(text=s1.text)

    def parse_qz_data(self, resp, code, name):
        '''
        解析权重页面
        :return:
        '''
        logger.info(code)
        qz_stock_list = resp.xpath(
            '//div[@class="details_r fr"]//table[@class="table table-even table-bg p_table tc"]/tbody/tr')

        qz_list = []
        for stock in qz_stock_list:
            s_code = stock.xpath('.//td[1]/text()').extract_first()
            s_name = stock.xpath('.//td[2]/text()').extract_first()
            s_area = stock.xpath('.//td[3]/text()').extract_first()
            s_qz = stock.xpath('.//td[4]/text()').extract_first()
            try:
                s_qz = float(s_qz)
            except:
                pass

            d = {}
            d['代码'] = s_code
            d['名称'] = s_name
            d['行业'] = s_area
            d['权重'] = s_qz
            qz_list.append(d)

        qz_dict = {}
        qz_dict['ETF代码'] = code
        qz_dict['ETF名称'] = name
        qz_dict['权重'] = qz_list
        return qz_dict

    def more_etf_product(self,resp):
        more_detail_url = resp.xpath('//div[@class="details_l fl"]/h2[@class="t_3 pr mb-10"]/a/@href').extract_first()
        r = requests.get(more_detail_url,headers={'User-Agent': 'Molliza Firefox Chrome'})


    def etf_product_list(self, resp_selector):
        tables = resp_selector.xpath('//table[@class="table table-even table-bg p_table tc mb-20"]/tbody/tr')
        if len(tables) == 0:
            return []
        product_list = []
        for item in tables:
            product_list.append(item.xpath('.//td/text()').extract_first())

        return product_list

    def store_product_list(self, code, name, products):
        if len(products) == 0:
            return []

        return {'etf_code': code, 'etf_name': name, 'etf_product': products, 'crawltime': str(datetime.date.today())}

    def etf_detail_constituent_stock(self, sess, code, name):
        '''
        获取某个基金的权重数据
        :param sess:
        :param code:
        :param name:
        :return:
        '''

        self.download_excel_file(sess, code, name)
        resp = self.get_qz_page(sess, code)
        detail_data_json = self.parse_qz_data(resp, code, name)
        self.store_data(detail_data_json, collection_name='etf_quanzhong',key='ETF代码')

        product_list = self.etf_product_list(resp)
        if len(product_list)==5:
            product_list = self.store_product_list(code, name, product_list)
            self.store_data(product_list, collection_name='etf_product',key='etf_code')
        else:
            product_list = self.store_product_list(code, name, product_list)
            if product_list:
                self.store_data(product_list, collection_name='etf_product',key='etf_code')

    def store_data(self, detail_data_json, collection_name, key=''):

        try:
            if not self.db[collection_name].find_one({key: detail_data_json[key]}):
                self.db[collection_name].insert_one(detail_data_json)
        except Exception as e:
            logger.error(e)
            return False
        else:
            return True


if __name__ == '__main__':
    app = IndexSpider(first_use=True)
    # app.basic_info()

    # app.full_market()

    app.etf_detail_with_product_inuse()
