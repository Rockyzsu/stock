import random
import re

import datetime
import demjson
import requests
import time

from settings import get_mysql_conn
# 基金数据爬虫

today = datetime.datetime.now().strftime('%Y-%m-%d')
headers = {
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'Accept': '*/*',
    'Referer': 'http://stockapp.finance.qq.com/mstats/?id=fund_close',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8',
}

conn = get_mysql_conn('db_fund', local='local')
cursor = conn.cursor()

create_table = 'create table if not EXISTS `{}` (`基金代码` varchar(20) PRIMARY KEY,`基金简称` varchar(100),`最新规模-万` float,`实时价格` float,`涨跌幅` float,`成交额-万` float,`单位净值` float,`累计净值` float,`折溢价率` float ,`申购状态` VARCHAR(20),`申赎状态` varchar(20),`基金经理` VARCHAR(200),`成立日期` VARCHAR(20), `管理人名称` VARCHAR(200));'.format(today)

cursor.execute(create_table)
conn.commit()

def fetch_fund_data():
    '''
    第一次运行
    :return:
    '''
    for p in range(1,114):
        print('page ',p)
        params = (
            ('appn', 'rank'),
            ('t', 'ranklof/chr'),
            ('p', p),
            ('o', '0'),
            ('l', '40'),
            ('v', 'list_data'),
        )
        session =requests.Session()
        response = session.get('http://stock.gtimg.cn/data/index.php', headers=headers, params=params, verify=False)
        ls_data = re.search('var list_data=(.*?);',response.text,re.S)
        ret = ls_data.group(1)
        js=demjson.decode(ret)
        detail_url = 'http://gu.qq.com/{}'
        query_string = js.get('data')
        time.sleep(5*random.random())

        insert_data = 'insert into `{}` VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'.format(today)
        check_code_exists = 'select count(*) from `{}` WHERE `基金代码`=%s'.format(today)

        for code in query_string.split(','):

            cursor.execute(check_code_exists,(code[2:]))
            ret = cursor.fetchone()
            if ret[0]>0:
                continue

            r = session.get(detail_url.format(code), headers=headers)
            search_str = re.search('<script>SSR\["hqpanel"\]=(.*?)</script>',r.text)
            # time.sleep(5*random.random())

            if search_str:
                s = search_str.group(1)
                js_ = demjson.decode(s)

                sub_js = js_.get('data').get('data').get('data')
                zxjg= sub_js.get('zxjg')
                jgzffd= sub_js.get('jgzffd')
                cj_total_amount= sub_js.get('cj_total_amount')

                zyjl= float(sub_js.get('zyjl',0))*100

                info =js_.get('data').get('data').get('info')
                jjdm=info.get('jjdm')
                jjjc=info.get('jjjc')
                zxgm=info.get('zxgm')
                dwjz=info.get('dwjz')
                ljjz=info.get('ljjz')
                sgzt=info.get('sgzt')
                shzt=info.get('shzt')
                jjjl=info.get('jjjl')
                clrq=info.get('clrq')
                glrmc=info.get('glrmc')

                try:
                    cursor.execute(insert_data,(jjdm,jjjc,float(zxgm),float(zxjg),float(jgzffd),float(cj_total_amount),float(dwjz),float(ljjz),float(zyjl),sgzt,shzt,jjjl,clrq,glrmc))
                except Exception as e:
                    print(e)
                    conn.rollback()
                else:
                    conn.commit()

if __name__=='__main__':
    fetch_fund_data()