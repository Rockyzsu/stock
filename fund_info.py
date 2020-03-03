import random
import re

import datetime
import demjson
import pymongo
import requests
import time
from realtme_jjjz import update_jj
from settings import get_mysql_conn
# 基金数据爬虫
now = datetime.datetime.now()
today = now.strftime('%Y-%m-%d')
_time = now.strftime('%H:%M:%S')

if _time< '11:30:00':
    today +='morning'
elif _time < '14:45:00':
    today +='noon'
else:
    today+='close'

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

def tencent_info():
    create_table = 'create table if not EXISTS `{}` (`基金代码` varchar(20) PRIMARY KEY,`基金简称` varchar(100),`最新规模-万` float,`实时价格` float,`涨跌幅` float,`成交额-万` float,`净值日期` VARCHAR(10),`单位净值` float,`累计净值` float,`折溢价率` float ,`申购状态` VARCHAR(20),`申赎状态` varchar(20),`基金经理` VARCHAR(200),`成立日期` VARCHAR(20), `管理人名称` VARCHAR(200),`更新时间` VARCHAR(20));'.format(today)

    cursor.execute(create_table)
    conn.commit()


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

        insert_data = 'insert into `{}` VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'.format(today)
        check_code_exists = 'select count(*) from `{}` WHERE `基金代码`=%s'.format(today)
        update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
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
                jzrq=info.get('jzrq')

                try:
                    cursor.execute(insert_data,(jjdm,jjjc,float(zxgm),float(zxjg),float(jgzffd),float(cj_total_amount),jzrq,float(dwjz),float(ljjz),float(zyjl),sgzt,shzt,jjjl,clrq,glrmc,update_time))
                except Exception as e:
                    print(e)
                    conn.rollback()
                else:
                    conn.commit()
    conn.close()

def jsl_fund_info():
    client = pymongo.MongoClient(host='192.168.10.48',port=17001)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    doc1 = client['fund_daily'][f'jsl_stock_lof_{today}']
    doc2 = client['fund_daily'][f'jsl_index_lof_{today}']

    url='https://www.jisilu.cn/data/lof/stock_lof_list/?___jsl=LST___t=1582355333844&rp=25'

    index_lof ='https://www.jisilu.cn/data/lof/index_lof_list/?___jsl=LST___t=1582356112906&rp=25'

    r = requests.get(url=url,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'})
    js = r.json()
    rows = js.get('rows')

    for item in rows:
        cell = item.get('cell')
        try:
            doc1.insert_one(cell)
        except Exception as e:
            print(e)

    r2 = requests.get(url=index_lof, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'})
    js = r2.json()
    rows = js.get('rows')

    for item in rows:
        cell = item.get('cell')
        try:
            doc2.insert_one(cell)
        except Exception as e:
            print(e)

if __name__=='__main__':

    start = time.time()
    tencent_info()
    jsl_fund_info()
    end=time.time()


    print('Time used: {}'.format(end-start))
    print(datetime.datetime.today())
    update_jj(today)
