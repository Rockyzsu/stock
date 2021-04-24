# -*- coding: utf-8 -*-
# website: http://30daydo.com
# @Time : 2020/8/26 19:58
# @File : ttjj.py

import sys
import execjs

sys.path.append('..')
import requests
import demjson
import datetime
import time
from pandas.core.frame import DataFrame
from bs4 import BeautifulSoup
import json
import re
import pandas as pd
from multiprocessing import Pool
import logging
from configure.settings import DBSelector
from common.BaseService import BaseService


def rank_data_crawl(time_interval='3n', ft='all'):
    # 当前日期
    td_str = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    td_dt = datetime.datetime.strptime(td_str, '%Y-%m-%d')
    # 去年今日
    last_dt = td_dt - datetime.timedelta(days=365)
    last_str = datetime.datetime.strftime(last_dt, '%Y-%m-%d')
    rank_url = 'http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft={0}&rs=&gs=0&sc={1}zf&st=desc&sd={2}&ed={3}&qdii=&tabSubtype=,,,,,&pi=1&pn=10000&dx=1'.format(
        ft, time_interval, last_str, td_str)
    # print(rank_url)
    headers = {}  # 需要配置
    rp = requests.get(rank_url, headers=headers)
    rank_txt = rp.text[rp.text.find('=') + 2:rp.text.rfind(';')]
    # print(rank_txt)
    # 数据
    rank_rawdata = demjson.decode(rank_txt)
    # rawdata_allNum = rank_rawdata['allNum']
    rank_list = []
    for i in rank_rawdata['datas']:
        rank_list.append(i.split(','))
    # print(rank_url, 'rawdata_allNum:{}'.format(rawdata_allNum), sep='\n')
    return rank_list


# 详情页面的抓取
def get_allFund_content(single_fund_url):
    try:
        # print(single_fund_url)
        # if infromation[3] !='理财型' and infromation[3] !='货币型' and infromation[2].endswith('(后端)')==False:
        #     code = infromation[0]
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
        r = requests.get(single_fund_url, headers=headers)
        r.encoding = r.apparent_encoding  # 避免中文乱码
        soup = BeautifulSoup(r.text, 'lxml')
        # # 判断交易状态
        # staticItem = soup.select('.staticItem')[0].get_text()
        # if '终止' in staticItem or '认购' in staticItem:
        #     pass
        # else:
        # 各项指标
        # 基金名、基金类型、单位净值、累计净值、基金规模、成立日、评级、基金涨幅及排名
        # （近1周、近1月、近3月、近6月、今年来、近1年、近2年、近3年）
        fund_code = single_fund_url[26:32]
        # fund_name = re.match('[\u4e00-\u9fffA-Za-z]+', soup.select('.fundDetail-tit > div')[0].get_text()).group()
        fund_name = soup.select('.SitePath > a')[2].get_text()
        unit_netValue = soup.select('.dataItem02 > .dataNums > span.ui-font-large')[0].get_text()
        accumulative_netValue = soup.select('.dataItem03 > .dataNums > span.ui-font-large')[0].get_text()
        fund_info = [i for i in soup.select('div.infoOfFund tr > td')]
        # fund_type1 = fund_info[0].get_text().split('：')[1].strip()
        fund_type = re.search('：[DQI\-\u4e00-\u9fffA]+', fund_info[0].get_text()).group()[1:]
        fund_scale = fund_info[1].get_text().split('：')[1].strip()
        fund_establishmentDate = fund_info[3].get_text().split('：')[1].strip()
        # fund_grade = fund_info[5].get_text().split('：')[1].strip()
        fund_Rdata = soup.select('#increaseAmount_stage > .ui-table-hover div.Rdata ')  # 指数基金多一排，考虑re或者排名倒着写
        fund_1weekAmount = fund_Rdata[0].get_text()
        fund_1monthAmount = fund_Rdata[1].get_text()
        fund_3monthAmount = fund_Rdata[2].get_text()
        fund_6monthAmount = fund_Rdata[3].get_text()
        fund_thisYearAmount = fund_Rdata[4].get_text()
        fund_1yearAmount = fund_Rdata[5].get_text()
        fund_2yearAmount = fund_Rdata[6].get_text()
        fund_3yearAmount = fund_Rdata[7].get_text()
        fund_1weekRank = fund_Rdata[-8].get_text()
        fund_1monthRank = fund_Rdata[-7].get_text()
        fund_3monthRank = fund_Rdata[-6].get_text()
        fund_6monthRank = fund_Rdata[-5].get_text()
        fund_thisYearRank = fund_Rdata[-4].get_text()
        fund_1yearRank = fund_Rdata[-3].get_text()
        fund_2yearRank = fund_Rdata[-2].get_text()
        fund_3yearRank = fund_Rdata[-1].get_text()
        Fund_data = [fund_code, fund_name, fund_type, unit_netValue, accumulative_netValue,
                     fund_scale, fund_establishmentDate,
                     fund_1weekAmount, fund_1monthAmount, fund_3monthAmount, fund_6monthAmount,
                     fund_thisYearAmount, fund_1yearAmount, fund_2yearAmount, fund_3yearAmount,
                     fund_1weekRank, fund_1monthRank, fund_3monthRank, fund_6monthRank, fund_thisYearRank,
                     fund_1yearRank, fund_2yearRank, fund_3yearRank]
        print(Fund_data)
        return Fund_data
    except Exception as e:
        # print('Error:', single_fund_url, str(e))
        logging.exception('Error:', single_fund_url, str(e))


def main():
    #  初始化区域
    main1_name = ['基金代码', '基金简称', '缩写', '日期', '单位净值', '累计净值',
                  '日增长率(%)', '近1周增幅', '近1月增幅', '近3月增幅', '近6月增幅', '近1年增幅', '近2年增幅', '近3年增幅',
                  '今年来', '成立来', '成立日期', '购买手续费折扣', '自定义', '手续费原价？', '手续费折后？',
                  '布吉岛', '布吉岛', '布吉岛', '布吉岛']
    # main1_name = ['基金代码', '基金简称', '日期', '单位净值', '累计净值',
    #               '日增长率(%)', '近1周增幅', '近1月增幅', '近3月增幅', '近6月增幅', '近1年增幅', '近2年增幅', '近3年增幅',
    #               '今年来', '成立来', '成立日期']
    main2_name = ['基金代码', '基金简称', '基金类型', '单位净值', '累计净值', '基金规模', '成立日期', \
                  '近1周增幅', '近1月增幅', '近3月增幅', '近6月增幅', '今年来增幅', '近1年增幅', '近2年增幅', '近3年增幅', \
                  '近1周排名', '近1月排名', '近3月排名', '近6月排名', '今年来排名', '近1年排名', '近2年排名', '近3年排名']
    # ########################## 先爬API接口 ###################################
    rawData = rank_data_crawl()
    # 数据清洗
    # 未满三年剔除
    rawData = DataFrame(rawData, columns=main1_name)
    rawData = rawData.loc[rawData['近3年增幅'] != '']
    # 去除无用列
    # # rawData.drop(rawData.columns(['缩写', '购买手续费折扣', '自定义', '手续费原价？', '手续费折后？', '布吉岛'], axis=1))
    # rawData.drop(['缩写', '购买手续费折扣', '自定义', '手续费原价？', '手续费折后？', '布吉岛'], axis=1, inplace=True)
    rawData1 = rawData.iloc[1:15, [0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]]
    # main1_name = main1_name[0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]

    # ########################## 单页面抓取 ###################################
    # 获取抓取的detail网址
    detail_urls_list = ['http://fund.eastmoney.com/{}.html'.format(i) for i in rawData1['基金代码']]
    print('#详情页面的抓取#启动时间：', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    middle = datetime.datetime.now()
    # 多线程
    p = Pool(4)
    all_fund_data = p.map(get_allFund_content, detail_urls_list)
    p.close()
    p.join()
    while None in all_fund_data:
        all_fund_data.remove(None)
    end = datetime.datetime.now()
    print('#详情页面的抓取#用时：', str(end - middle))
    print('程序结束时间：', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    all_fund_data = DataFrame(all_fund_data, columns=main2_name)

    # 表合并
    data_merge = pd.merge(rawData1, all_fund_data, how='left', on='基金代码')

    # 文件储存
    file_content = pd.DataFrame(columns=main1_name, data=rawData)
    file_content.to_csv('rawDATA-{}.csv'.format(time.strftime("%Y-%m-%d", time.localtime())), encoding='gbk')


class TTFund(BaseService):

    def __init__(self):
        super(TTFund,self).__init__()
        self.ft_dict={'混合':'hh', # 类型 gp： 股票 hh： 混合
                 '股票':'gp',
                 'qdii':'qdii',
                 'lof':'lof',
                 'fof':'fof',
                 '指数':'zs'
                 }

        self.doc = self.mongo()['db_stock']['ttjj_rank']

    @property
    def headers(self):
        return {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7",
            "Cache-Control": "no-cache",
            "Cookie": "AUTH_FUND.EASTMONEY.COM_GSJZ=AUTH*TTJJ*TOKEN; em_hq_fls=js; HAList=a-sh-603707-%u5065%u53CB%u80A1%u4EFD%2Ca-sz-300999-%u91D1%u9F99%u9C7C%2Ca-sh-605338-%u5DF4%u6BD4%u98DF%u54C1%2Ca-sh-600837-%u6D77%u901A%u8BC1%u5238%2Ca-sh-600030-%u4E2D%u4FE1%u8BC1%u5238%2Ca-sz-300059-%u4E1C%u65B9%u8D22%u5BCC%2Cd-hk-06185; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; qgqp_b_id=956b72f8de13e912a4fc731a7845a6f8; searchbar_code=163407_588080_501077_163406_001665_001664_007049_004433_005827_110011; EMFUND0=null; EMFUND5=02-24%2019%3A30%3A19@%23%24%u5357%u65B9%u6709%u8272%u91D1%u5C5EETF%u8054%u63A5C@%23%24004433; EMFUND6=02-24%2021%3A46%3A42@%23%24%u5357%u65B9%u4E2D%u8BC1%u7533%u4E07%u6709%u8272%u91D1%u5C5EETF@%23%24512400; EMFUND7=02-24%2021%3A58%3A27@%23%24%u6613%u65B9%u8FBE%u84DD%u7B79%u7CBE%u9009%u6DF7%u5408@%23%24005827; EMFUND8=03-05%2015%3A33%3A29@%23%24%u6613%u65B9%u8FBE%u4E2D%u5C0F%u76D8%u6DF7%u5408@%23%24110011; EMFUND9=03-05 23:47:41@#$%u5929%u5F18%u4F59%u989D%u5B9D%u8D27%u5E01@%23%24000198; ASP.NET_SessionId=ntwtbzdkb0vpkzvil2a3h1ip; st_si=44251094035925; st_asi=delete; st_pvi=77351447730109; st_sp=2020-08-16%2015%3A54%3A02; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=3; st_psi=20210309200219784-0-8081344721",
            "Host": "fund.eastmoney.com",
            "Pragma": "no-cache",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://fund.eastmoney.com/data/fundranking.html",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36",
        }

    def mongo(self):
        return DBSelector().mongo('qq')

    def start(self):
        time_interval='jnzf' # jnzf:今年以来 3n: 3年

        key='混合'
        self.category_rank(key,time_interval)

    def category_rank(self,key,time_interval):
        ft=self.ft_dict[key]
        td_str = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
        td_dt = datetime.datetime.strptime(td_str, '%Y-%m-%d')
        # 去年今日
        last_dt = td_dt - datetime.timedelta(days=365)
        last_str = datetime.datetime.strftime(last_dt, '%Y-%m-%d')
        # rank_url = 'http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft={0}&rs=&gs=0&sc={1}zf&st=desc&sd={2}&ed={3}&qdii=&tabSubtype=,,,,,&pi=1&pn=10000&dx=1'.format(
        #     ft, time_interval, last_str, td_str)
        rank_url='http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft={0}&rs=&gs=0&sc={1}&st=desc&sd={2}&ed={3}&qdii=&tabSubtype=,,,,,&pi=1&pn=10000&dx=1'.format(ft, time_interval, last_str, td_str)
        content = self.get(url=rank_url)

        rank_data = self.parse(content)
        rank_list = self.key_remap(rank_data,key)
        self.save_data(rank_list)

    def save_data(self,rank_list):
        try:
            self.doc.insert_many(rank_list)
        except Exception as e:
            print(e)

    def parse(self, content):
        js_content = execjs.compile(content)
        rank = js_content.eval("rankData")
        return rank.get('datas',[])

    def key_remap(self,rank_data,type_):
        '''
        映射key value
        '''
        # print(rank_data)
        colums=['基金代码', '基金简称', '缩写', '日期', '单位净值', '累计净值',
         '日增长率(%)', '近1周增幅', '近1月增幅', '近3月增幅', '近6月增幅', '近1年增幅', '近2年增幅', '近3年增幅',
         '今年来', '成立来', '成立日期', '购买手续费折扣', '自定义', '手续费原价？', '手续费折后？',
         '布吉岛1', '布吉岛2', '布吉岛3', '布吉岛4']
        return_rank_data=[]
        for rank in rank_data:
            rand_dict={}
            rand_dict['type']=type_
            rand_dict['crawl_date']=self.today
            rank_ = rank.split(',')
            for index,colum in enumerate(colums):
                rand_dict[colum]=rank_[index]
            return_rank_data.append(rand_dict)

        return return_rank_data

if __name__ == '__main__':
    # main()
    app = TTFund()
    app.start()
