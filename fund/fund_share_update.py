"# -*- coding"
import re

"""
@author:xda
@file:fund_share_update.py
@time:2021/01/20
"""
# 基金份额
import sys

sys.path.append('..')
from configure.settings import DBSelector, send_from_aliyun
from common.BaseService import BaseService
from configure.util import notify
import requests
import warnings
import datetime

warnings.filterwarnings("ignore")

from sqlalchemy import Column, String, create_engine, INTEGER, VARCHAR, DATE,DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类:
Base = declarative_base()


class FundBaseInfoModel(Base):
    # 表的名字:
    __tablename__ = 'LOF_BaseInfo'

    # 表的结构:
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    code = Column(VARCHAR(6), comment='基金代码')
    name = Column(VARCHAR(40), comment='基金名称')
    category = Column(VARCHAR(8), comment='基金类别')
    invest_type = Column(VARCHAR(6), comment='投资类别')
    manager_name = Column(VARCHAR(48), comment='管理人呢名称')
    issue_date = Column(DATE, comment='上市日期')
    crawltime = Column(DateTime,comment='爬取日期')


# class ShareModel(Base):
#     # 表的名字:
#     __tablename__ = 'LOF_Share'
#
#     # 表的结构:
#     id = Column(String(20), primary_key=True)
#     name = Column(String(20))
#     fund_category = Column()


class FundShare(BaseService):

    def __init__(self, first_use=False):
        super(FundShare, self).__init__(f'../log/{self.__class__.__name__}.log')
        # self.create_table()
        self.headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Host": "fund.szse.cn",
            "Pragma": "no-cache",
            "Referer": "http://fund.szse.cn/marketdata/fundslist/index.html?catalogId=1000_lf&selectJjlb=ETF",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
            "X-Request-Type": "ajax",
            "X-Requested-With": "XMLHttpRequest",
        }
        self.url = 'http://fund.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1000_lf&TABKEY=tab1&PAGENO={}&selectJjlb=LOF&random=0.019172632634173903'
        self.session = requests.Session()
        self.logger.info('start...sz fund')
        self.LAST_TEXT = ''
        self.engine = self.get_engine()
        if first_use:
            self.create_table()

        self.db_session = self.get_session()
        self.sess = self.db_session()


    def get_engine(self):
        return DBSelector().get_engine('db_stock')

    def create_table(self):
        # 初始化数据库连接:

        Base.metadata.create_all(self.engine)  # 创建表结构

    def get_session(self):

        return sessionmaker(bind=self.engine)

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
        self.execute(insert_data, (
            jjdm, jjjc, zxgm, zxjg, jgzffd,
            cj_total_amount, jzrq, dwjz,
            ljjz,
            zyjl, sgzt, shzt, jjjl, clrq,
            glrmc, is_realtime, update_time), conn, self.logger)

    def check_exist(self, code):
        check_code_exists = 'select count(*) from `{}` WHERE `基金代码`=%s'.format(TODAY)
        cursor.execute(check_code_exists, (code[2:]))
        ret = cursor.fetchone()
        return ret

    def get(self, url, retry=5, js=True):
        start = 0
        while start < retry:
            try:
                response = self.session.get(url, headers=self.headers,
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
            self.logger.error('重试太多')
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
            if content is None:
                continue

            if content == self.LAST_TEXT:
                break

            self.LAST_TEXT = content

            ls_data = re.search('var list_data=(.*?);', content, re.S)

            if ls_data:
                ret = ls_data.group(1)
            else:
                self.logger.error('解析出错')
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
                if content is None:
                    self.logger.error('请求内容为空')
                    continue

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
        self.execute(add_column1, (), conn, self.logger)
        self.execute(add_column2, (), conn, self.logger)

    def get_fund_info(self, table):
        query = 'select `基金代码`,`基金简称`,`实时价格` from `{}`'.format(table)
        return self.execute(query, (), conn, self.logger)

    def udpate_db(self, table, jz, yjl, is_realtime, code):
        update_sql = 'update `{}` set `实时净值`= %s,`溢价率`=%s ,`实时估值`=%s where  `基金代码`=%s'.format(table)
        self.execute(update_sql, (jz, yjl, is_realtime, code), conn, self.logger)

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
            jz, yjl, is_realtime, code = self.get_netvalue(table, item)
            self.udpate_db(table, jz, yjl, is_realtime, code)
            print(f'更新代码{code}')

        self.logger.info('更新成功')

    def get_netvalue(self, table, item):
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
                if js is None or realtime_price is None:
                    yjl = 0
                else:
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
        query_sql = '''select `基金代码`,`基金简称`,`实时价格`,`实时净值`,`溢价率`,`净值日期` from `{}` where `申购状态`='开放' and `申赎状态`='开放' and `基金简称` not like '%%债%%' and `溢价率` is not null and !(`实时价格`=1 and `涨跌幅`=0 and `成交额-万`=0) order by `溢价率` {} limit 10'''.format(
            today, order)
        return self.execute(query_sql, (), conn, self.logger)

    def html_formator(self, ret, html):

        for row in ret:
            html += f'<tr><td>{row[0]}</td><td>{row[1].replace("(LOF)", "")}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td></tr>'
        html += '</table></div>'
        return html

    def combine_html(self, html, today):

        body = '<div><table border="1">' \
               '<tr><th>基金代码</th><th>基金简称</th><th>实时价格</th><th>实时净值</th><th>溢价率</th><th>净值日期</th></tr>'

        html += body
        result_asc = self.query_fund_data(today, 'asc')
        if self.check_content(result_asc):
            html = self.html_formator(result_asc, html)

        html += body

        result_desc = self.query_fund_data(today, 'desc')
        if self.check_content(result_desc):
            html = self.html_formator(result_desc, html)

        return html

    def check_content(self, content):
        if content is None:
            self.logger.error('获取内容为空')
            return False
        else:
            return True

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

    def json_parse(self, js_data):
        data = js_data[0].get('data', [])

        if not data:
            self.stop = True
            return None

        for item in data:
            jjlb = item['jjlb']
            tzlb = item['tzlb']  #
            ssrq = item['ssrq']

            name = self.extract_name(item['jjjcurl'])

            dqgm = self.convert_number(item['dqgm'])  # 当前规模

            glrmc = self.extract_glrmc(item['glrmc'])  # 管理人名称

            code = self.extract_code(item['sys_key'])

            yield (jjlb, tzlb, ssrq, dqgm, glrmc, code, name)

    def extract_name(self, name):
        return re.search('<u>(.*?)</u>', name).group(1)

    def extract_code(self, code):
        return re.search('<u>(\d{6})</u>', code).group(1)

    def extract_glrmc(self, glrmc):
        if re.search(('\<a.*?\>(.*?)\</a\>'), glrmc):
            glrmc = re.search(('\<a.*?\>(.*?)\</a\>'), glrmc).group(1).strip()
        return glrmc

    def model_process(self, jjlb, tzlb, ssrq, dqgm, glrmc, code, name):
        print(jjlb, tzlb, ssrq, dqgm, glrmc, code)
        obj = FundBaseInfoModel(
            code=code,
            name=name,
            category=jjlb,
            invest_type=tzlb,
            manager_name=glrmc,
            issue_date=ssrq,
        )

        self.sess.add(obj)
        self.sess.commit()

    def convert_number(self, s):
        return float(s.replace(',', ''))

    def run(self):
        page = 1
        self.stop = False
        while not self.stop:
            content = self.get(self.url.format(page))
            for item in self.json_parse(content):
                self.model_process(*item)

            page += 1


if __name__ == '__main__':
    app = FundShare(first_use=True)
    app.run()
