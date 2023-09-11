# 上交所 公告
import datetime
import re
import sys
import os
sys.path.append('..')
from configure.settings import DBSelector
import requests
from loguru import logger

logger.add('../log/jucao_retis_notice.log')

ROOT = '/root/datahub/jucao/'

class SHTradingAnnounce:

    def __init__(self):
        self.client = DBSelector().mongo('qq')

    def _crawl(self, kw, page):
        import requests

        cookies = {
            'JSESSIONID': '76E27FF3E4AC2BAFBB469054B6F323A2',
            '_sp_ses.2141': '*',
            'routeId': '.uc2',
            '_sp_id.2141': '12a4755f-69a7-43e9-826b-d425c0bb343f.1672993315.1.1672993426.1672993315.19f199ad-b61b-4e7e-84c0-b78d2bde6fec',
        }

        headers = {
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'http://www.cninfo.com.cn',
            'Referer': 'http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&lastPage=index',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            # 'Cookie': 'JSESSIONID=76E27FF3E4AC2BAFBB469054B6F323A2; _sp_ses.2141=*; routeId=.uc2; _sp_id.2141=12a4755f-69a7-43e9-826b-d425c0bb343f.1672993315.1.1672993426.1672993315.19f199ad-b61b-4e7e-84c0-b78d2bde6fec',
        }

        data = {
            'pageNum': str(page),
            'pageSize': '30',
            'column': 'fund',
            'tabName': 'fulltext',
            'plate': '',
            'stock': '',
            'searchkey': kw,
            'secid': '',
            'category': '',
            'trade': '',
            'seDate': '',
            'sortName': '',
            'sortType': '',
            'isHLtitle': 'true',
        }

        response = requests.post(
            'http://www.cninfo.com.cn/new/hisAnnouncement/query',
            cookies=cookies,
            headers=headers,
            data=data,
            verify=False,
        )

        return response.json()

    def parse(self):
        return self.content['announcements']

    def total_count(self):
        return self.content['totalRecordNum']

    def insert_item(self, doc):
        try:
            if not self.client['db_stock']['retis_notice'].find_one({'announcementId':doc['announcementId']}):
                logger.info('item not in mongodb, insert')
                self.client['db_stock']['retis_notice'].insert_one(doc)
        except Exception as e:
            logger.error(e)

    def filter_unname_char(self,name):

        return re.sub('[\/:*?"<>|]','',name)

    def download_pdf(self):
        if self.client['db_stock']['retis_notice'].count_documents({'downloaded':{'$exists':False}})>0:
            pdf_urls = self.client['db_stock']['retis_notice'].find({'downloaded':{'$exists':False}})
            for item in pdf_urls:

                secName = item['secName']
                announcementTitle = self.filter_unname_char(item['announcementTitle'])
                url = item['PDF_URL']
                m = re.search('/(\d{4})-(\d{2})-(\d{2})/',url)
                if m:
                    date = '{}-{}-{}'.format(m.group(1),m.group(2),m.group(3))
                else:
                    date= item['updated'].strftime('%Y-%m-%d')

                save_filename = '{}-{}-{}'.format(date,secName,announcementTitle)
                if len(save_filename)>=50:
                    save_filename = save_filename[:50]
                    save_filename+='.pdf'


                r = requests.get(url,headers={'User-Agent':'chrome firefox'})

                full_path = os.path.join(ROOT, save_filename)
                with open(full_path,'wb') as fp:
                    fp.write(r.content)
                    self.client['db_stock']['retis_notice'].update_one({'announcementId':item['announcementId']},{'$set':{'downloaded':True,'filename':save_filename}})

    def dumpmongo(self, announce_list):
        host = 'http://static.cninfo.com.cn/'

        for item in announce_list:
            item['PDF_URL'] = host + item['adjunctUrl']
            item['updated'] = datetime.datetime.now()
            self.insert_item(item)


    def run(self):
        PAGE=3
        for p in range(1,PAGE):
            self.content = self._crawl('基础设施', p)
            if self.total_count()>0:
                data = self.parse()
                self.dumpmongo(data)


if __name__ == '__main__':
    app = SHTradingAnnounce()
    app.run()
    app.download_pdf()
