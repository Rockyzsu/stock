import random
import re
import datetime
import demjson
import requests
import time
import sys
sys.path.append('..')
from configure.settings import DBSelector,  send_from_aliyun
from common.BaseService import BaseService
from configure.util import notify

# 基金数据爬虫

now = datetime.datetime.now()
TODAY = now.strftime('%Y-%m-%d')
_time = now.strftime('%H:%M:%S')

if _time < '11:30:00':
    TODAY += 'morning'
elif _time < '14:45:00':
    TODAY += 'noon'
else:
    TODAY += 'close'

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


class FundSpider(BaseService):

    def __init__(self):
        super(FundSpider, self).__init__(f'../log/{self.__class__.__name__}.log')
        self.create_table()
        self.session = requests.Session()
        self.logger.info('start...')

    def create_table(self):
        create_table = 'create table if not EXISTS `{}` (`基金代码` varchar(20) PRIMARY KEY,`基金简称` ' \
                       'varchar(100),`最新规模-万` float,' \
                       '`实时价格` float,`涨跌幅` float,`成交额-万` float,' \
                       '`净值日期` VARCHAR(10),`单位净值` float,`累计净值` ' \
                       'float,`折溢价率` float ,`申购状态` VARCHAR(20),`申赎状态` varchar(20),' \
                       '`基金经理` VARCHAR(200),' \
                       '`成立日期` VARCHAR(20), `管理人名称` VARCHAR(200),' \
                       '`实时估值` INT,`更新时间` VARCHAR(20));'.format(
            TODAY)

        self.execute(create_table,(),conn)

    def convert(self, float_str):

        try:
            return_float = float(float_str)
        except:
            return_float = None
        return return_float

    def insert_data(self, jjdm, jjjc, zxgm, zxjg, jgzffd, cj_total_amount, jzrq, dwjz, ljjz, zyjl, sgzt, shzt, jjjl,
                    clrq, glrmc):

        update_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        is_realtime = 1
        zxgm = self.convert(zxgm)
        zxjg = self.convert(zxjg)
        jgzffd = self.convert(jgzffd)
        cj_total_amount = self.convert(cj_total_amount)
        dwjz = self.convert(dwjz)
        ljjz = self.convert(ljjz)
        zyjl = self.convert(zyjl)

        insert_data = 'insert into `{}` VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'.format(TODAY)
        self.execute(insert_data,(
                jjdm, jjjc, zxgm, zxjg, jgzffd,
                cj_total_amount, jzrq, dwjz,
                ljjz,
                zyjl, sgzt, shzt, jjjl, clrq,
                glrmc, is_realtime, update_time),conn)


    def check_exist(self, code):
        check_code_exists = 'select count(*) from `{}` WHERE `基金代码`=%s'.format(TODAY)
        cursor.execute(check_code_exists, (code[2:]))
        ret = cursor.fetchone()
        return ret

    def get(self, url, params, retry=5, js=False):
        start = 0
        while start < retry:
            try:
                response = self.session.get(url, headers=headers, params=params,
                                            verify=False)
            except Exception as e:
                self.logger.error(e)
                start += 1

            else:
                if js:
                    content = response.json()
                else:
                    content = response.text

                return content

        if start == retry:
            return None

    def crawl(self):
        code_set = set()
        url = 'http://stock.gtimg.cn/data/index.php'

        for p in range(1, MAX_PAGE):

            params = (
                ('appn', 'rank'),
                ('t', 'ranklof/chr'),
                ('p', p),
                ('o', '0'),
                ('l', '40'),
                ('v', 'list_data'),
            )

            content = self.get(url, params)
            ls_data = re.search('var list_data=(.*?);', content, re.S)

            if ls_data:
                ret = ls_data.group(1)
            else:
                continue

            js = demjson.decode(ret)  # 解析json的库
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

                detail_url = 'http://gu.qq.com/{}'
                content = self.get(url=detail_url.format(code), params=None)
                self.parse_content_and_save(content)

    def parse_content_and_save(self, content):

        jjdm, jjjc, zxgm, zxjg, jgzffd, cj_total_amount, jzrq, dwjz, ljjz, zyjl, sgzt, shzt, jjjl, clrq, glrmc = self.parse_html(
            content)
        self.insert_data(jjdm, jjjc, zxgm, zxjg, jgzffd, cj_total_amount, jzrq, dwjz, ljjz, zyjl, sgzt,
                         shzt, jjjl, clrq, glrmc)

    def parse_html(self, content):
        search_str = re.search('<script>SSR\["hqpanel"\]=(.*?)</script>', content)

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
            return jjdm, jjjc, zxgm, zxjg, jgzffd, cj_total_amount, jzrq, dwjz, ljjz, zyjl, sgzt, shzt, jjjl, clrq, glrmc

    def change_table_field(self, table):
        add_column1 = 'alter table `{}` add column `实时净值` float'.format(table)
        add_column2 = 'alter table `{}` add column `溢价率` float'.format(table)
        self.execute(add_column1,(),conn)
        self.execute(add_column2,(),conn)


    def get_fund_info(self, table):
        query = 'select `基金代码`,`基金简称`,`实时价格` from `{}`'.format(table)
        return self.execute(query,(),conn)

    def udpate_db(self, table, jz, yjl, is_realtime, code):
        update_sql = 'update `{}` set `实时净值`= %s,`溢价率`=%s ,`实时估值`=%s where  `基金代码`=%s'.format(table)
        self.execute(update_sql, (jz, yjl, is_realtime, code),conn)

    def update_netvalue(self, table):
        '''
        更新净值
        :param table:
        :return:
        '''
        # table='2020-02-25' # 用于获取code列
        # TODAY=datetime.datetime.now().strftime('%Y-%m-%d')
        self.change_table_field(table)

        all_fund_info = self.get_fund_info(table)

        for item in all_fund_info:
           jz, yjl, is_realtime, code = self.get_netvalue(table,item)
           self.udpate_db(table, jz, yjl, is_realtime, code)

        self.logger.info('更新成功')

    def get_netvalue(self,table,item):
        # 获取净值
        code = item[0]
        is_realtime = 1
        realtime_price = item[2]

        url = 'http://web.ifzq.gtimg.cn/fund/newfund/fundSsgz/getSsgz?app=web&symbol=jj{}'
        js = self.get(url=url.format(code), params=None, js=True)
        data = js.get('data')

        if data:

            try:
                data_list = data.get('data')
            except Exception as e:
                self.logger.error(e)
                jz = None
                yjl = None

            else:
                last_one = data_list[-1]
                jz = last_one[1]
                yjl = -1 * round((jz - realtime_price) / realtime_price * 100, 2)

        else:
            is_realtime = 0
            yjl, jz = self.get_fund(table, code)

        return jz, yjl, is_realtime, code


    def get_fund(self, table, code):
        query = f'select `折溢价率`,`单位净值` from `{table}` where `基金代码`=%s'
        cursor.execute(query, code)
        ret = cursor.fetchone()
        yjl, jz = ret[0], ret[1]
        yjl = round(yjl, 3)
        jz = round(jz, 3)
        return yjl, jz

    def query_fund_data(self, today, order):
        query_sql = '''select `基金代码`,`基金简称`,`实时价格`,`实时净值`,`溢价率`,`净值日期` from `{}` where `申购状态`='开放' and `申赎状态`='开放' and `溢价率` is not null and !(`实时价格`=1 and `涨跌幅`=0 and `成交额-万`=0) order by `溢价率` {} limit 10'''.format(
            today, order)
        return self.execute(query_sql,(),conn)

    def html_formator(self, ret, html):

        for row in ret:
            html += f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>'
        html += '</table></div>'
        return html

    def combine_html(self, html, today):

        body = '<div><table border="1">' \
               '<tr><th>基金代码</th><th>基金简称</th><th>实时价格</th><th>实时净值</th><th>溢价率</th><th>净值日期</th></tr>'

        html += body
        result_asc = self.query_fund_data(today, 'asc')
        html = self.html_formator(result_asc,html )

        html += body

        result_desc = self.query_fund_data(today, 'desc')
        html = self.html_formator(result_desc,html )
        return html

    def notice_me(self, today):

        now = datetime.datetime.now()

        if now.hour > NOTIFY_HOUR:
            # 下午才会发通知

            title = f'{today} 基金折溢价'

            html = ''
            html = self.combine_html(html, TODAY)

            try:
                send_from_aliyun(title, html, types='html')
            except Exception as e:
                self.logger.error(e)
                self.logger.info('发送失败')
            else:
                self.logger.info('发送成功')


class JSLFund(BaseService):
    '''
    集思录的指数
    '''

    def __init__(self):
        super(JSLFund, self).__init__(f'../log/{self.__class__.__name__}.log')

        client = DB.mongo(location_type='qq',async_type=False)

        self.jsl_stock_lof = client['fund_daily'][f'jsl_stock_lof_{self.today}']
        self.jsl_index_lof = client['fund_daily'][f'jsl_index_lof_{self.today}']

        self.stock_url = 'https://www.jisilu.cn/data/lof/stock_lof_list/?___jsl=LST___t=1582355333844&rp=25'
        self.index_lof_url = 'https://www.jisilu.cn/data/lof/index_lof_list/?___jsl=LST___t=1582356112906&rp=25'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'}

        self.logger.info(f'start...')

    def get(self, url, retry=5):

        start = 0
        while start < retry:
            try:
                r = requests.get(
                    url=url,
                    headers=self.headers)
            except Exception as e:
                self.logger.error(e)
                start += 1

            else:
                js = r.json()
                return js

        if start == retry:
            return None

    def crawl(self):
        self.parse_json(types='stock')
        self.parse_json(types='index')

    def parse_json(self, types):

        if types == 'stock':
            url = self.stock_url
            mongo_doc = self.jsl_stock_lof
        else:
            url = self.index_lof_url
            mongo_doc = self.jsl_index_lof

        return_js = self.get(url=url)
        rows = return_js.get('rows')

        for item in rows:
            cell = item.get('cell')
            try:
                mongo_doc.insert_one(cell)
            except Exception as e:
                self.logger.error(e)
                notify(title='入mongo出错',desp=f'{self.__class__} 写入mongodb出错')


def main():
    tencent_spider = FundSpider()
    tencent_spider.crawl()
    tencent_spider.update_netvalue(TODAY)
    tencent_spider.notice_me(TODAY)

    jsl_spider = JSLFund()
    jsl_spider.crawl()


if __name__ == '__main__':
    main()
