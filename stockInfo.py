# working v1.0
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
import json
import datetime
import time
import codecs
import os, sys
import requests
import re
from scrapy.selector import Selector
from elasticsearch import Elasticsearch
from configure.settings import llogger

logger = llogger('log/stockinfo.log')

my_useragent = [
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
    'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)'
]

es = Elasticsearch('10.18.6.102:9200')

def create_tb(conn):
    cur = conn.cursor()
    cmd = '''CREATE TABLE IF NOT EXISTS tb_cnstock(Date DATETIME ,Title VARCHAR (800),URL VARCHAR (100),PRIMARY KEY (URL)) charset=utf8;'''
    try:
        cur.execute(cmd)
        conn.commit()
        return True
    except Exception as e:
        logger.info(e)
        conn.rollback()
        return False


def getinfo(days=-30):
    last_day = datetime.datetime.now() + datetime.timedelta(days=days)

    url = "http://app.cnstock.com/api/waterfall?callback=jQuery19107348148582372209_1557710326005&colunm=qmt-tjd_ggkx&page={}&num=20&showstock=0"

    page = 1
    temp_time = time.strftime("[%Y-%m-%d]-[%H-%M]", time.localtime())

    store_filename = "StockNews-%s.log" % temp_time

    f_open = codecs.open(store_filename, 'w', 'utf-8')
    db_name = 'db_stock'

    conn = get_mysql_conn(db_name, local='local')

    cur = conn.cursor()

    run_flag = True

    while run_flag:
        headers = {'Referer': 'http://ggjd.cnstock.com/company/scp_ggjd/tjd_ggkx',
                   'User-Agent': 'Mozilla/5.0 (Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36', }

        retry = 3
        response = None

        for _ in range(retry):
            try:
                response = requests.get(url=url.format(page), headers=headers)
                response.encoding = 'utf8'
            except Exception as e:
                if hasattr(e, 'code'):
                    logger.info("error code %d" % e.code)
                elif hasattr(e, 'reason'):
                    logger.info("error reason %s " % e.reason)
                time.sleep(5)
            else:
                if response.status_code == 200:
                    break

        try:
            text = response.text.encode('utf8').decode('unicode_escape')
            js = re.search('jQuery19107348148582372209_1557710326005\((.*?)\)$', text, re.S).group(1)
            js = re.sub('\r\n', '', js)
            js_data = json.loads(js)

        except Exception as e:
            logger.error(e)
            return None

        content = js_data.get('data', {}).get('item', {})

        if content is None:
            continue

        for item in content:
            title = item.get('title')

            if '晚间重要公告集锦' in title or '停复牌汇总' in title:
                continue

            link = item.get('link')
            link = link.replace('\\', '')
            pubdate_t = item.get('time')
            pubdate_dtype = datetime.datetime.strptime(pubdate_t, '%Y-%m-%d %H:%M:%S')

            if pubdate_dtype < last_day:
                run_flag = False

            keyword = item.get('keyword')
            if keyword:
                keyword = ' '.join(keyword)

            sub_content = None

            for i in range(2):
                try:
                    sub_content = requests.get(url=link, headers=headers)

                except Exception as e:
                    logger.error(e)
                    continue
                    # 重试

                else:
                    if sub_content.status_code == 200:
                        break

            root = Selector(text=sub_content.text)
            detail_content = root.xpath('//div[@id="qmt_content_div"]')[0].xpath('string(.)').extract_first()
            if detail_content:
                detail_content = detail_content.strip()
            temp_tuple = (pubdate_dtype, title, link, detail_content, keyword)
            insert_sql = 'insert into tb_cnstock (Date,Title,URL,Content,keyword) values (%s,%s,%s,%s,%s)'

            # es
            try:
                pubdate_dtype=pubdate_dtype.strftime("%Y-%m-%d"'T'"%H:%M:%S")
                body = {'Title': title, 'ULR': link, 'keyword': keyword, 'content': detail_content, 'Date': pubdate_dtype}

                es.index(index='cnstock',doc_type='doc',body=body)

            except Exception as e:
                logger.error(e)

            # mysql
            try:
                cur.execute(insert_sql, temp_tuple)
                conn.commit()
            except Exception as e:
                logger.error(e)
                conn.rollback()

            file_content = '{} ---- {}\n{}\n\n'.format(pubdate_t, title, link)
            f_open.write(file_content)

        page += 1

    f_open.close()


if __name__ == "__main__":

    sub_folder = DATA_PATH
    if not os.path.exists(sub_folder):
        os.mkdir(sub_folder)
    os.chdir(sub_folder)

    if len(sys.argv) > 1:
        if re.match('-\d+', sys.argv[1]):
            day = int(sys.argv[1])
        else:
            day = -3
    else:
        day = -3

    getinfo(days=day)
    # fetch_detail()
