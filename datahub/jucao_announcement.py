# -*- coding: utf-8 -*-
# @Time : 2021/4/21 0:35
# @File : jucao_announcement.py
# @Author : Rocky C@www.30daydo.com

# 巨潮公告
import datetime
import re
import sys
sys.path.append('..')
from common.BaseService import BaseService
from configure.settings import DBSelector


class JuCaoAnnouncement(BaseService):

    def __init__(self,param=None):
        super(JuCaoAnnouncement, self).__init__('../log/jucao.log')

        self.enableFilter=False # 不过滤关键标题

        self.base_url = 'http://www.cninfo.com.cn/new/hisAnnouncement/query'

        self.params_dict={'季报':'category_jdbg_jjgg',
                          '年报':'category_ndbg_jjgg',
                          '申购赎回':'category_sgsh_jjgg',
                          '其它':'category_qt_jjgg',
                          '基本信息变更':'category_jbxxbg_jjgg',
                            '招募设立':'category_jjzm_jjgg',
                          '中报':'category_bndbg_jjgg',
                          '分红':'category_fh_jjgg',
                          '持有人大会':'category_fecyr_jjgg',
                          '净值':'category_jzgg_jjgg',
                          '组合投资':'category_zhtz_jjgg',
                          '基金经理变更':'category_ggjjjl_jjgg'
                          }
        if param is None:
            kw = ';'.join(list(self.params_dict.values()))
        else:
            kw=self.params_dict.get(param)

        self.params = {
            "pageNum": "1",
            "pageSize": "30",
            "column": "fund",
            "tabName": "fulltext",
            "plate": "",
            "stock": "",
            "searchkey": "",
            "secid": "",
            # 申购等数据 category_qt_jjgg 其他 ； 基本信息变更；申购赎回；持有人大会 ; 基金招募
            # "category": "category_jbxxbg_jjgg;category_fecyr_jjgg;category_sgsh_jjgg;category_qt_jjgg;category_jjzm_jjgg",
            "category": kw,
            "trade": "",
            "seDate": self.gen_date_param(),
            "sortName": "",
            "sortType": "",
            "isHLtitle": "false",
        }

        self.pdf_base = 'http://static.cninfo.com.cn/{}'
        self.doc = DBSelector().mongo('qq')['db_stock']['jucao_announcement']

    def gen_date_param(self):
        '''
        日期查询字符
        '''
        current = datetime.datetime.now()
        last_day = current + datetime.timedelta(days=1)
        current_str = self.time_str(current)
        last_day_str = self.time_str(last_day)

        # 可以自定义时间
        # current_str='2021-04-01'
        # last_day_str='2021-04-14'
        x='{}~{}'.format(current_str,last_day_str)
        return x


    @property
    def headers(self):
        __headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": "JSESSIONID=65041C569E0AB62716DE7A3E56D5D6DD; _sp_ses.2141=*; routeId=.uc2; SID=6db1a040-5ecc-4c43-b7ea-ad1fd3796c54; _sp_id.2141=65aeab49-b3df-4bc2-b54c-5e55ac099012.1617809813.2.1618936057.1617810063.81c5fd00-91e2-417e-beb7-b5277a3f8390",
            "Host": "www.cninfo.com.cn",
            "Origin": "http://www.cninfo.com.cn",
            "Referer": "http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&lastPage=index",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
        }
        return __headers

    def start(self):
        total_page = self.get_total_page
        self.logger.info(f'共有{total_page}页公告')
        self.fetch_all_page_data(total_page)

    @property
    def ignore_str_list(self):
        '''
        排除的标题字符
        '''
        filter_str = [
            '(第\d+季度报告)','(季度报告)','(年度报告)','(说明书)','(销售机构的公告)','(费率优惠)','(流动性服务商)','(关联方承销证券)'
        ]
        return '|'.join(filter_str)

    def fetch_all_page_data(self,pages):
        for i in range(1,pages+1):
            # print(i)
            self.single_page_analysis(i)

    def single_page_analysis(self,i):

        post_data = self.params.copy()
        post_data['pageNum']=str(i)

        try:
            response = self.post(
            url=self.base_url,
            post_data=post_data,
            _json=True,
        )
        except Exception as e:
            self.logger.error(e)
            self.logger.error(post_data)
            return

        announcements_list = response.get('announcements',None)
        if  announcements_list is not None and len(announcements_list)>0:
            announcements_data = self.parse_item(response.get('announcements'))
            self.batch_mongodb(announcements_data)

    def batch_mongodb(self,announce_data):
        for item in announce_data:
            announcementId = item['announcementId']
            try:
                ret = self.doc.update_one({'announcementId':announcementId},{'$setOnInsert':item},upsert=True)
                # self.logger.info(ret.matched_count,ret.modified_count)
            except Exception as e:
                self.logger.error(e)

    def parse_item(self,js_data):
        return_url_list = []
        for item in js_data:
            title=item['announcementTitle']
            pattern = re.compile(self.ignore_str_list)
            # pattern = re.compile('['+self.ignore_str_list+']')
            m=re.search(pattern,title)

            if m and self.enableFilter:
                # 过滤不想要的标题，不关心的
                continue

            fund_info_dict ={}
            adjunctUrl=item['adjunctUrl']
            fund_info_dict['code']=item['secCode']
            fund_info_dict['title']=title
            fund_info_dict['announcementId']=item['announcementId']
            fund_info_dict['secName']=item['secName']
            fund_info_dict['announcementType']=item['announcementType']
            fund_info_dict['announcementTime']=self.convert_timestamp(item['announcementTime']) #ts 转为 date str
            fund_info_dict['crawltime']=datetime.datetime.now()
            detail_url = self.pdf_base.format(adjunctUrl)
            fund_info_dict['url']=detail_url
            return_url_list.append(fund_info_dict)

        return return_url_list

    @property
    def get_total_page(self):
        post_data = self.params.copy()
        content = self.post(
            url=self.base_url,
            post_data=post_data,
            _json=True,
        )
        return int(content.get('totalAnnouncement')/30)



def main():
    app = JuCaoAnnouncement()
    app.start()


if __name__ == '__main__':
    main()
