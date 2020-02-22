# -*- coding: utf-8 -*-
# website: http://30daydo.com
# @Time : 2020/2/20 17:06
# @File : etf_info.py
# 获取etf的成分股数据
import pymongo
import re
import requests
from scrapy.selector import Selector
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from config import mysql_password
from sqlalchemy import Column, Integer, String, DateTime, FLOAT
from sqlalchemy.orm import sessionmaker

engine = create_engine(f"mysql+pymysql://root:{mysql_password}@127.0.0.1:3306/db_stock")
Base = declarative_base()


class IndexObject(Base):
    __tablename__ = 'tb_etf_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    代码 = Column(String(10), unique=True)
    详细URL = Column(String(100), unique=False)
    指数名称 = Column(String(20), unique=True)
    股票数目 = Column(String(10), unique=False)
    最新收盘 = Column(FLOAT, unique=False)
    一个月收益率 = Column(FLOAT, unique=False)
    资产类别 = Column(String(20), unique=False)
    热点 = Column(String(20), unique=False)
    地区覆盖 = Column(String(20), unique=False)
    币种 = Column(String(20), unique=False)
    定制 = Column(String(20), unique=False)
    指数类别 = Column(String(20), unique=False)


class IndexObjectNew(Base):
    __tablename__ = 'etf_info'

    id = Column(Integer, primary_key=True,autoincrement=True)
    代码 = Column(String(10), unique=True)
    # 详细URL = Column(String(100), unique=False)
    指数名称 = Column(String(60), unique=False)
    指数英文名称 = Column(String(100), unique=False)
    股票数目 = Column(String(10), unique=False)
    最新收盘 = Column(FLOAT, unique=False)
    一个月收益率 = Column(FLOAT, unique=False)

    基准点数 = Column(String(20), unique=False)
    指数介绍 = Column(String(300), unique=False)
    指数全称 = Column(String(100), unique=False)

    资产类别 = Column(String(20), unique=False)
    指数系列 = Column(String(20), unique=False)

    热点 = Column(String(20), unique=False)
    地区覆盖 = Column(String(20), unique=False)
    指数类别 = Column(String(20), unique=False)

class IndexObjectSZ(Base):
    __tablename__ = 'etf_info_sz'

    id = Column(Integer, primary_key=True,autoincrement=True)
    代码 = Column(String(20), unique=True)
    指数名称 = Column(String(100), unique=False)
    详细URL = Column(String(200), unique=False)

    基日 = Column(String(20), unique=False)
    基日指数 = Column(String(20), unique=False)
    起始计算日 = Column(String(20), unique=False)



def crawl():
    '''
    拿到的只是上证的数据
    :return:
    '''
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
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
            最新收盘=price,
            一个月收益率=month_ratio,
            资产类别=type_,
            热点=hot_pot,
            地区覆盖=area,
            币种=coin,
            定制=specified,
            指数类别=index_type
        )

        try:
            session.add(obj)

            session.commit()
        except Exception as e:
            print(e)
            session.rollback()


def full_market():
    total = 1630
    page_size = 50
    total_page = total // page_size + 1
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

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
            )

            try:
                session.add(obj)

                session.commit()
            except Exception as e:
                print(e)
                session.rollback()

def get_detail():
    client = pymongo.MongoClient()
    doc = client['fund']['etf_info']
    Session = sessionmaker(bind=engine)
    session = Session()
    ret = session.query(IndexObjectNew).all()
    download_url ='http://www.csindex.com.cn/uploads/file/autofile/cons/{}cons.xls'
    sess = requests.Session()
    for i in ret:
        code = i.代码
        s=sess.get(download_url.format(code),headers={'User-Agent': 'Molliza Firefox Chrome'})
        name = i.指数名称

        with open('data/{}_{}.xls'.format(code,name),'wb') as f:
            f.write(s.content)


        # 获取权重
        qz_url = 'http://www.csindex.com.cn/zh-CN/indices/index-detail/{}'
        s1=sess.get(qz_url.format(code),headers={'User-Agent': 'Molliza Firefox Chrome'})
        resp = Selector(text=s1.text)
        qz_stock_list = resp.xpath('//div[@class="details_r fr"]//table[@class="table table-even table-bg p_table tc"]/tbody/tr')
        qz_list=[]
        for stock in qz_stock_list:
            s_code = stock.xpath('.//td[1]/text()').extract_first()
            s_name = stock.xpath('.//td[2]/text()').extract_first()
            s_area = stock.xpath('.//td[3]/text()').extract_first()
            s_qz = stock.xpath('.//td[4]/text()').extract_first()
            d={}
            d['代码']=s_code
            d['名称']=s_name
            d['行业']=s_area
            d['权重']=s_qz
            qz_list.append(d)
        t={}
        t['ETF代码']=code
        t['ETF名称']=name
        t['权重']=qz_list
        try:
            doc.insert_one(t)
        except Exception as e:
            print(e)


def szse_etf():
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    sess = requests.Session()
    url='http://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1812_zs&TABKEY=tab1&PAGENO={}&random=0.4572618756063547'
    for i in range(1,10):
        s= sess.get(url=url.format(i),headers={'User-Agent': 'Molliza Firefox Chrome'})
        ret = s.json()
        if len(ret)>0:
            data = ret[0].get('data')
            for d in data:
                zsdm=d.get('zsdm')
                zsmc=d.get('zsmc')

                code = re.search('<u>(.*?)</u>',zsdm).group(1)
                detail_url = re.search('href=\'(.*?)\'',zsdm).group(1)
                name = re.search('<u>(.*?)</u>', zsmc).group(1)

                jrnew=d.get('jrnew')
                jrzs=d.get('jrzs')
                qsrnew=d.get('qsrnew')

                obj = IndexObjectSZ(
                    代码=code,
                指数名称 = name,
                详细URL = detail_url,

                基日 = jrnew,
                基日指数 = jrzs,
                起始计算日 = qsrnew,
                )

                session.add(obj)
                session.commit()

def szse_etf_detail():
    client = pymongo.MongoClient()
    doc = client['fund']['etf_info_sz']

    Session = sessionmaker(bind=engine)
    session = Session()
    ret = session.query(IndexObjectSZ).all()
    sess = requests.Session()
    url='http://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1747_zs&TABKEY=tab1&ZSDM={}&random=0.5790989240667317'

    sub_url ='http://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1747_zs&TABKEY=tab1&PAGENO={}&ZSDM={}&random=0.29981446895718666'
    for item in ret:
        code = item.代码
        name = item.指数名称
        r = sess.get(url.format(code),headers={'User-Agent': 'Molliza Firefox Chrome'})
        js = r.json()
        t={}
        t['指数代码']=code
        t['指数名称']=name
        t_list=[]

        if js is not None and len(js)>0:
            data = js[0]
            page = data.get('metadata',{}).get('pagecount',0)
            for i in range(1,page+1):
                s1=sess.get(url=sub_url.format(i,code),headers={'User-Agent': 'Molliza Firefox Chrome'})
                r1=s1.json()
                if r1 is not None and len(r1) > 0:
                    stock_list = r1[0].get('data')
                    for st in stock_list:
                        zqdm=st.get('zqdm')
                        zqjc=st.get('zqjc')
                        zgb=st.get('zgb') # 总股本
                        ltgb=st.get('ltgb') # 流通股本
                        hylb=st.get('hylb') #
                        nrzsjs=st.get('nrzsjs')
                        d={}
                        d['证券代码']=zqdm
                        d['证券简称']=zqjc
                        d['总股本']=zgb
                        d['流通股本']=ltgb
                        d['行业列表']=hylb
                        d['nrzsjs']=nrzsjs
                        t_list.append(d)
        t['成分股数据']=t_list

        try:
            doc.insert_one(t)
        except Exception as e:
            print(e)



if __name__ == '__main__':
    # crawl()
    # full_market()
    # get_detail()
    # szse_etf()
    szse_etf_detail()
    print('done')
