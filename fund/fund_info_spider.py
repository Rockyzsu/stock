import random
import re
import datetime
import demjson
import os
import pymongo
import requests
import time
import sys

sys.path.append('..')
from settings import DBSelector, _json_data, send_from_aliyun, llogger

# 基金数据爬虫

now = datetime.datetime.now()
today = now.strftime('%Y-%m-%d')
_time = now.strftime('%H:%M:%S')

if _time < '11:30:00':
    today += 'morning'
elif _time < '14:45:00':
    today += 'noon'
else:
    today += 'close'

NOTIFY_HOUR = 13
MAX_PAGE = 114

headers = {
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'Accept': '*/*',
    # 'Referer': 'http://stockapp.finance.qq.com/mstats/?id=fund_close',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8',
}

DB = DBSelector()
conn = DB.get_mysql_conn('db_fund', 'qq')
cursor = conn.cursor()
base_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(base_dir, '..', 'log')
logger = llogger(os.path.join(log_path, 'fund_info.log'))


class FundSpider(object):

    def __init__(self):
        self.create_tb()

    def create_tb(self):
        create_table = 'create table if not EXISTS `{}` (`基金代码` varchar(20) PRIMARY KEY,`基金简称` varchar(100),`最新规模-万` float,' \
                       '`实时价格` float,`涨跌幅` float,`成交额-万` float,`净值日期` VARCHAR(10),`单位净值` float,`累计净值` float,`折溢价率` float ,`申购状态` VARCHAR(20),`申赎状态` varchar(20),`基金经理` VARCHAR(200),' \
                       '`成立日期` VARCHAR(20), `管理人名称` VARCHAR(200),`实时估值` INT,`QDII` INT ,`更新时间` VARCHAR(20));'.format(
            today)
        try:
            cursor.execute(create_table)
        except Exception as e:
            conn.rollback()
            print(e)
        else:
            conn.commit()

    def convert(self, float_str):
        try:
            return_float = float(float_str)
        except:
            return_float = None
        return return_float

    def insert_data(self, jjdm, jjjc, zxgm, zxjg, jgzffd, cj_total_amount, jzrq, dwjz, ljjz, zyjl, sgzt, shzt, jjjl,
                    clrq, glrmc):
        insert_data = 'insert into `{}` VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'.format(today)
        update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        is_realtime = 1
        zxgm = self.convert(zxgm)
        zxjg = self.convert(zxjg)
        jgzffd = self.convert(jgzffd)
        cj_total_amount = self.convert(cj_total_amount)
        dwjz = self.convert(dwjz)
        ljjz = self.convert(ljjz)
        zyjl = self.convert(zyjl)

        try:
            cursor.execute(insert_data, (
                jjdm, jjjc, zxgm, zxjg, jgzffd, cj_total_amount, jzrq, dwjz,
                ljjz,
                zyjl, sgzt, shzt, jjjl, clrq, glrmc, is_realtime, update_time))
        except Exception as e:
            logger.info(e)
            conn.rollback()
        else:
            conn.commit()

    def check_exist(self, code):
        check_code_exists = 'select count(*) from `{}` WHERE `基金代码`=%s'.format(today)

        cursor.execute(check_code_exists, (code[2:]))
        ret = cursor.fetchone()
        return ret

    def crawl(self):
        code_set = set()
        for p in range(1, MAX_PAGE):
            params = (
                ('appn', 'rank'),
                ('t', 'ranklof/chr'),
                ('p', p),
                ('o', '0'),
                ('l', '40'),
                ('v', 'list_data'),
            )

            session = requests.Session()
            response = session.get('http://stock.gtimg.cn/data/index.php', headers=headers, params=params, verify=False)
            ls_data = re.search('var list_data=(.*?);', response.text, re.S)

            if ls_data:
                ret = ls_data.group(1)

            js = demjson.decode(ret) # 解析json的库
            detail_url = 'http://gu.qq.com/{}'
            query_string = js.get('data')
            time.sleep(5 * random.random())

            for code in query_string.split(','):
                if code not in code_set:
                    code_set.add(code)
                else:
                    continue

                ret = self.check_exist(code)
                if ret[0] > 0:
                    continue
                try:
                    r = session.get(detail_url.format(code), headers=headers)
                except:
                    time.sleep(10)
                    try:
                        r = session.get(detail_url.format(code), headers=headers)
                    except:
                        continue

                search_str = re.search('<script>SSR\["hqpanel"\]=(.*?)</script>', r.text)

                if search_str:
                    s = search_str.group(1)
                    js_ = demjson.decode(s)

                    sub_js = js_.get('data').get('data').get('data')
                    zxjg = sub_js.get('zxjg')
                    jgzffd = sub_js.get('jgzffd')
                    cj_total_amount = sub_js.get('cj_total_amount')

                    zyjl = float(sub_js.get('zyjl', 0)) * 100

                    info = js_.get('data').get('data').get('info')
                    jjdm = info.get('jjdm')
                    jjjc = info.get('jjjc')
                    zxgm = info.get('zxgm')
                    dwjz = info.get('dwjz')
                    ljjz = info.get('ljjz')
                    sgzt = info.get('sgzt')
                    shzt = info.get('shzt')
                    jjjl = info.get('jjjl')
                    clrq = info.get('clrq')
                    glrmc = info.get('glrmc')
                    jzrq = info.get('jzrq')
                    self.insert_data(jjdm, jjjc, zxgm, zxjg, jgzffd, cj_total_amount, jzrq, dwjz, ljjz, zyjl, sgzt,
                                     shzt, jjjl, clrq, glrmc)

    def change_table_field(self, table):
        add_column1 = 'alter table `{}` add column `实时净值` float'.format(table)
        add_column2 = 'alter table `{}` add column `溢价率` float'.format(table)
        try:
            cursor.execute(add_column1)
        except Exception as e:
            logger.error(e)
            conn.rollback()
        else:
            conn.commit()

        try:
            cursor.execute(add_column2)
        except Exception as e:
            logger.error(e)
            conn.rollback()
        else:
            conn.commit()

    def get_fund_info(self, table):
        query = 'select `基金代码`,`基金简称`,`实时价格` from `{}`'.format(table)
        cursor.execute(query)
        ret = cursor.fetchall()
        return ret

    def udpate_db(self, table, jz, yjl, is_realtime, code):
        update_sql = 'update `{}` set `实时净值`= %s,`溢价率`=%s ,`实时估值`=%s where  `基金代码`=%s'.format(table)
        cursor.execute(update_sql, (jz, yjl, is_realtime, code))
        conn.commit()

    def update_jinzhi(self, table):
        '''
        更新净值
        :param table:
        :return:
        '''
        # table='2020-02-25' # 用于获取code列
        # today=datetime.datetime.now().strftime('%Y-%m-%d')
        self.change_table_field(table)

        url = 'http://web.ifzq.gtimg.cn/fund/newfund/fundSsgz/getSsgz?app=web&symbol=jj{}'
        session = requests.Session()
        ret = self.get_fund_info(table)

        for item in ret:
            code = item[0]
            is_realtime = 1
            realtime_price = item[2]
            try:
                resp = session.get(url.format(code), headers=headers)
            except:
                time.sleep(5)
                try:
                    resp = session.get(url.format(code), headers=headers)
                except:
                    continue

            js = resp.json()
            data = js.get('data')
            if data:
                try:
                    data_list = data.get('data')
                except Exception as e:
                    logger.error(e)
                    continue

                else:
                    last_one = data_list[-1]
                    jz = last_one[1]
                    yjl = -1 * round((jz - realtime_price) / realtime_price * 100, 2)

            else:
                is_realtime = 0
                yjl, jz = self.get_jj(table, code)

            self.udpate_db(table, jz, yjl, is_realtime, code)

        logger.info('更新成功')

    def get_jj(self, table, code):
        query = f'select `折溢价率`,`单位净值` from `{table}` where `基金代码`=%s'
        cursor.execute(query, code)
        ret = cursor.fetchone()
        yjl, jz = ret[0], ret[1]
        yjl = round(yjl, 3)
        jz = round(jz, 3)
        return yjl, jz

    def notify(self, today):

        now = datetime.datetime.now()

        if now.hour > NOTIFY_HOUR:
            # 下午才会发通知
            query_sql = '''select `基金代码`,`基金简称`,`实时价格`,`实时净值`,`溢价率`,`净值日期` from `{}` where `申购状态`='开放' and `申赎状态`='开放' and !(`实时价格`=1 and `涨跌幅`=0 and `成交额-万`=0) order by `溢价率` limit 10'''.format(
                today)
            cursor.execute(query_sql)
            ret = cursor.fetchall()
            html = '<div><table border="1">' \
                   '<tr><th>基金代码</th><th>基金简称</th><th>实时价格</th><th>实时净值</th><th>溢价率</th><th>净值日期</th></tr>'
            for i in ret:
                html += f'<tr><td>{i[0]}</td><td>{i[1]}</td><td>{i[2]}</td><td>{i[3]}</td><td>{i[4]}</td></tr>'
            html += '</table></div>'

            query_sql = '''select `基金代码`,`基金简称`,`实时价格`,`实时净值`,`溢价率`,`净值日期` from `{}` where `申购状态`='开放' and `申赎状态`='开放'  and `溢价率` is not null and !(`实时价格`=1 and `涨跌幅`=0 and `成交额-万`=0) order by `溢价率` desc limit 10'''.format(
                today)
            cursor.execute(query_sql)
            ret = cursor.fetchall()
            html += '<div><table border="1">' \
                    '<tr><th>基金代码</th><th>基金简称</th><th>实时价格</th><th>实时净值</th><th>溢价率</th><th>净值日期</th></tr>'
            for i in ret:
                html += f'<tr><td>{i[0]}</td><td>{i[1]}</td><td>{i[2]}</td><td>{i[3]}</td><td>{i[4]}</td><td>{i[5]}</td></tr>'
            html += '</table></div>'

            title = f'{today} 基金折溢价'

            try:
                send_from_aliyun(title, html, types='html')
            except Exception as e:
                logger.error(e)
                logger.info('发送失败')
            else:
                logger.info('发送成功')


class JSLFund(object):
    '''
    集思录的指数
    '''

    def __init__(self):

        host = _json_data['mongo']['qq']['host']
        # host='127.0.0.1'
        port = _json_data['mongo']['qq']['port']
        user = _json_data['mongo']['qq']['user']
        password = _json_data['mongo']['qq']['password']
        connect_uri = f'mongodb://{user}:{password}@{host}:{port}'
        client = pymongo.MongoClient(connect_uri)
        today_ = datetime.datetime.now().strftime('%Y-%m-%d')
        self.doc1 = client['fund_daily'][f'jsl_stock_lof_{today_}']
        self.doc2 = client['fund_daily'][f'jsl_index_lof_{today_}']

        self.url = 'https://www.jisilu.cn/data/lof/stock_lof_list/?___jsl=LST___t=1582355333844&rp=25'
        self.index_lof = 'https://www.jisilu.cn/data/lof/index_lof_list/?___jsl=LST___t=1582356112906&rp=25'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

    def crawl(self):

        r = requests.get(
            url=self.url,
            headers=self.headers)

        js = r.json()
        rows = js.get('rows')

        for item in rows:
            cell = item.get('cell')
            try:
                self.doc1.insert_one(cell)
            except Exception as e:
                logger.error(e)

        r2 = requests.get(
            url=self.index_lof,
            headers=self.headers)

        js = r2.json()
        rows = js.get('rows')

        for item in rows:
            cell = item.get('cell')
            try:
                self.doc2.insert_one(cell)
            except Exception as e:
                logger.error(e)


if __name__ == '__main__':
    tencent_spider = FundSpider()
    tencent_spider.crawl()
    tencent_spider.update_jinzhi(today)
    tencent_spider.notify(today)

    jsl_spider = JSLFund()
    jsl_spider.crawl()
