# working v1.0
from bs4 import BeautifulSoup
import datetime
import time
import codecs
import random
import os, sys
import requests
import re
from lxml import etree
from setting import llogger, get_mysql_conn, DATA_PATH

logger = llogger(__file__)
# headers={'User-Agent': 'Mozilla/5.0 (6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'}
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


# 把以前的内容抓取下来
def fetch_detail():
    db_name = 'db_stock'
    conn = get_mysql_conn(db_name, local='local')
    cursor = conn.cursor()
    query_sql = '''
    select * from tb_cnstock where Content is null;
    '''
    user_agent = random.choice(my_useragent)
    headers = {'User-Agent': user_agent, 'Host': "ggjd.cnstock.com", 'DNT': '1',
               'Accept': 'text/html, application/xhtml+xml, */*', }

    cursor.execute(query_sql)
    ret = cursor.fetchall()
    for item in ret:
        url = item[2]
        if url:
            url = url.strip()
            try:
                r = requests.get(url=url, headers=headers)
            except Exception as e:
                logger.error(e)
                continue

            else:
                root = etree.HTML(r.text)
                try:
                    string_list = root.xpath('//div[@class="main-content text-large"]')[0].xpath('string(.)')
                except Exception as e:
                    print(url)
                    print(e)
                    continue
                # content = ' '.join(string_list)
                content = string_list.strip()
                content = re.sub('缩小文字', '', content)
                content = re.sub('放大文字', '', content)
                content = content.strip()

                update_sql = '''
                                update tb_cnstock set Content = %s where URL = %s    
                            '''
                try:
                    cursor.execute(update_sql, (content, url))
                    conn.commit()
                except Exception as e:
                    print(e)
                    logger.error(e)
                    conn.rollback()


def getinfo(max_index_use=4, days=-30):
    last_day = datetime.datetime.now() + datetime.timedelta(days=days)
    stock_news_site = "http://ggjd.cnstock.com/gglist/search/ggkx/"

    index = 0
    max_index = max_index_use
    num = 1
    temp_time = time.strftime("[%Y-%m-%d]-[%H-%M]", time.localtime())

    store_filename = "StockNews-%s.log" % temp_time

    f_open = codecs.open(store_filename, 'w', 'utf-8')
    all_contents = []
    cmd_list = []
    db_name = 'db_stock'

    conn = get_mysql_conn(db_name, local='local')

    cur = conn.cursor()

    while index <= max_index:
        user_agent = random.choice(my_useragent)
        company_news_site = stock_news_site + str(index)
        headers = {'User-Agent': user_agent, 'Host': "ggjd.cnstock.com", 'DNT': '1',
                   'Accept': 'text/html, application/xhtml+xml, */*', }

        raw_content = ""
        retry = 6
        for _ in range(retry):
            try:
                req = requests.get(url=company_news_site, headers=headers)

            except Exception as e:
                if hasattr(e, 'code'):
                    logger.info("error code %d" % e.code)
                elif hasattr(e, 'reason'):
                    logger.info("error reason %s " % e.reason)
            else:
                if req:
                    raw_content = req.text
                    break

        if raw_content is None:
            return

        try:
            soup = BeautifulSoup(raw_content, "html.parser")
            all_content = soup.find_all("span", "time")
        except Exception as e:
            logger.info(e)
            return None

        for i in all_content:
            news_time = i.string
            node = i.next_sibling

            url = node['href']
            try:
                year = re.findall('tjd_ggkx/(\d+)/', url)[0][:4]
            except Exception as e:
                continue
            news_time_f = datetime.datetime.strptime(year + '-' + news_time, '%Y-%m-%d %H:%M')

            if news_time_f >= last_day:
                str_temp = "No.%s \n%s\t%s\n---> %s \n\n" % (str(num), news_time, node['title'], node['href'])



                all_contents.append(str_temp)

                f_open.write(str_temp)

                url = url.strip()
                try:
                    r = requests.get(url=url, headers=headers)
                except Exception as e:
                    logger.error(e)
                    continue

                root = etree.HTML(r.text)
                try:
                    string_list = root.xpath('//div[@class="main-content text-large"]')[0].xpath('string(.)')
                except Exception as e:
                    print(url)
                    print(e)
                    string_list=''

                # content = ' '.join(string_list)
                content = string_list.strip()
                content = re.sub('缩小文字', '', content)
                content = re.sub('放大文字', '', content)
                content = content.strip()


                cmd = '''INSERT INTO tb_cnstock (Date,Title,URL,Content) VALUES(\'%s\',\'%s\',\'%s\',\'%s\');''' % (
                    news_time_f, node['title'].strip(), node['href'].strip(),content)
                cmd_list.append(cmd)

            num = num + 1
            # itchat.send(str_temp,toUserName=username)
            # time.sleep(1)
            # print("index %d" %index)
        index = index + 1

    f_open.close()
    # if len(all_contents) > 0:
    #     sendmail(''.join(all_contents), temp_time)


    for i in cmd_list:
        logger.info(i)

        try:
            cur.execute(i)
            conn.commit()

        except Exception as e:
            logger.info(e)
            conn.rollback()
            continue

    conn.close()


if __name__ == "__main__":

    sub_folder = DATA_PATH
    if not os.path.exists(sub_folder):
        os.mkdir(sub_folder)
    os.chdir(sub_folder)

    if len(sys.argv) > 1:
        if re.match('-\d+', sys.argv[1]):
            day = int(sys.argv[1])
        else:
            day = -2
    else:
        day = -2

    getinfo(days=day)
    # fetch_detail()
