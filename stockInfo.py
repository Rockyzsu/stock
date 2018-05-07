import re

__author__ = 'rocchen'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
# working v1.0
from bs4 import BeautifulSoup
import urllib2
import datetime
import time
import codecs
import random
import os, sys
# import itchat
# import MySQLdb
# import setting
from setting import sendmail,LLogger
from setting import get_mysql_conn
logger = LLogger('news.log')

def create_tb(conn):
    cur=conn.cursor()
    cmd = '''CREATE TABLE IF NOT EXISTS tb_cnstock(Date DATETIME ,Title VARCHAR (80),URL VARCHAR (80),PRIMARY KEY (URL)) charset=utf8;'''
    try:
        cur.execute(cmd)
        conn.commit()
        # conn.close()
        return True
    except Exception, e:
        logger.log(e)
        conn.rollback()
        return False

def getinfo(max_index_user=3, days=-2):
    last_day = datetime.datetime.now() + datetime.timedelta(days=days)
    stock_news_site = "http://ggjd.cnstock.com/gglist/search/ggkx/"

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
        'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)']
    index = 0
    max_index = max_index_user
    num = 1
    temp_time = time.strftime("[%Y-%m-%d]-[%H-%M]", time.localtime())

    store_filename = "StockNews-%s.log" % temp_time

    f_open = codecs.open(store_filename, 'w', 'utf-8')
    all_contents = []
    cmd_list=[]
    while index <= max_index:
        user_agent = random.choice(my_useragent)
        # print user_agent
        company_news_site = stock_news_site + str(index)
        # content = urllib2.urlopen(company_news_site)
        headers = {'User-Agent': user_agent, 'Host': "ggjd.cnstock.com", 'DNT': '1',
                   'Accept': 'text/html, application/xhtml+xml, */*', }

        req = urllib2.Request(url=company_news_site, headers=headers)
        resp = None
        raw_content = ""
        retry=6
        for _ in range(retry):
            try:
                resp = urllib2.urlopen(req, timeout=30)

            except urllib2.HTTPError as e:
                e.fp.read()
            except urllib2.URLError as e:
                if hasattr(e, 'code'):
                    logger.log("error code %d" % e.code)
                elif hasattr(e, 'reason'):
                    logger.log("error reason %s " % e.reason)

            finally:
                if resp:
                    raw_content = resp.read()
                    break
        try:
            soup = BeautifulSoup(raw_content, "html.parser")
            all_content = soup.find_all("span", "time")
        except Exception,e:
            logger.log(e)
            return None
        # cmd_list = []
        for i in all_content:
            news_time = i.string
            # print news_time
            node = i.next_sibling

            url=node['href']
            try:
                year = re.findall('tjd_ggkx/(\d+)/',url)[0][:4]
            except Exception,e:
                continue
            news_time_f = datetime.datetime.strptime(year +'-' +news_time, '%Y-%m-%d %H:%M')

            if news_time_f >= last_day:
                # news_time_f=news_time_f.replace(2018)
                # print news_time_f
                str_temp = "No.%s \n%s\t%s\n---> %s \n\n" % (str(num), news_time, node['title'], node['href'])
                # print "inside %d" %num
                # print str_temp
                cmd = '''INSERT INTO tb_cnstock (Date,Title,URL ) VALUES(\'%s\',\'%s\',\'%s\');''' % (
                    news_time_f, node['title'].strip(), node['href'].strip())
                # print cmd
                cmd_list.append(cmd)
                # try:
                #     cur.execute(cmd)
                #     conn.commit()
                # except Exception, e:
                #     print e
                #     conn.rollback()

                all_contents.append(str_temp)

                f_open.write(str_temp)
            num = num + 1
            # itchat.send(str_temp,toUserName=username)
            # time.sleep(1)
            # print "index %d" %index
        index = index + 1

    f_open.close()
    if len(all_contents)>0:
        sendmail(''.join(all_contents), temp_time)

    db_name='db_stock'
    conn =get_mysql_conn(db_name,local=True)
    # create_tb(conn)
    cur = conn.cursor()
    for i in cmd_list:
        try:
            cur.execute(i)
            conn.commit()

        except Exception,e:
            logger.log(e)
            conn.rollback()

    conn.commit()
    # conn.close()

    db_name='qdm225205669_db'
    conn2=get_mysql_conn(db_name,local=False)
    # create_tb(conn2)
    cur2=conn2.cursor()
    for i in cmd_list:
        try:
            cur2.execute(i)
            conn2.commit()

        except Exception,e:
            print e
            conn2.rollback()
    conn2.commit()
    conn2.close()

    conn.close()

if __name__ == "__main__":

    sub_folder = os.path.join(os.path.dirname(__file__), "data")
    if not os.path.exists(sub_folder):
        os.mkdir(sub_folder)
    os.chdir(sub_folder)
    # itchat.auto_login(hotReload=True)
    # account = itchat.get_friends()
    # for i in account:
    #     if i[u'PYQuanPin'] == u'wei':
    #         username = i['UserName']
    if len(sys.argv) > 1:
        if re.match('-\d+',sys.argv[1]):
            day = int(sys.argv[1])
    else:
        day = -2
    # create_tb()
    getinfo(days=day)
    # print 'done'
