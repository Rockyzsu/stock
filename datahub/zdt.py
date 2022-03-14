# -*- coding=utf-8 -*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
# 每天的涨跌停
import sys
sys.path.append('..')
import re
import time
import os
# from configure.util import notify
from configure.settings import config_dict
import pandas as pd
from configure.settings import DBSelector
from configure.util import send_from_aliyun
import requests
import datetime
from common.BaseService import BaseService


class GetZDT(BaseService):

    def __init__(self, today=None):
        '''
        TODAY 格式 20200701
        :param today:
        '''
        super(GetZDT, self).__init__('log/zdt.log')

        if today:
            self.today = today
        else:
            self.today = time.strftime("%Y%m%d")

        self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36"
        self.path = config_dict('data_path')
        self.zdt_url = f'http://home.flashdata2.jrj.com.cn/limitStatistic/ztForce/{self.today}.js'
        self.zrzt_url = 'http://hqdata.jrj.com.cn/zrztjrbx/limitup.js'
        self.host = "home.flashdata2.jrj.com.cn"
        self.reference = "http://stock.jrj.com.cn/tzzs/zdtwdj/zdforce.shtml"

        self.header_zdt = {"User-Agent": self.user_agent,
                           "Host": self.host,
                           "Referer": self.reference}

        self.zdt_indexx = ['代码', '名称', '最新价格', '涨跌幅', '封成比', '封流比', '封单金额', '最后一次涨停时间', '第一次涨停时间', '打开次数',
                           '振幅',
                           '涨停强度']

        self.zrzt_indexx = ['序号', '代码', '名称', '昨日涨停时间', '最新价格', '今日涨幅', '最大涨幅', '最大跌幅', '是否连板', '连续涨停次数',
                            '昨日涨停强度', '今日涨停强度', '是否停牌', '昨天的日期', '昨日涨停价', '今日开盘价格', '今日开盘涨幅']
        self.header_zrzt = {"User-Agent": self.user_agent,
                            "Host": "hqdata.jrj.com.cn",
                            "Referer": "http://stock.jrj.com.cn/tzzs/zrztjrbx.shtml"
                            }

        self.DB = DBSelector()

    def download(self, url, headers, retry=5):

        for i in range(retry):
            try:
                resp = requests.get(url=url, headers=headers)
                content = resp.text
                md_check = re.findall('summary|lasttradedate', content)
                if content and len(md_check) > 0:
                    return content
                else:
                    time.sleep(60)
                    self.logger.info('failed to get content, retry: {}'.format(i))
                    continue
            except Exception as e:
                self.notify(title=f'{self.__class__}取涨跌停数据出错')
                self.logger.error(e)
                time.sleep(60)
                continue

        return None

    def convert_json(self, content):
        p = re.compile(r'"Data":(.*)};', re.S)
        if len(content) <= 0:
            self.logger.info('Content\'s length is 0')
            exit(0)
        result = p.findall(content)
        if result:
            try:
                t1 = result[0]
                t2 = re.sub('[\\r\\n]', '', t1)
                t2 = re.sub(',,', ',0,0', t2)
                t2 = re.sub('Infinity', '-1', t2)
                t2 = re.sub('NaN', '-1', t2)
                t2 = list(eval(t2))
                return t2
            except Exception as e:
                self.notify(title=f'{self.__class__}获取涨跌停数据出错')
                self.logger.info(e)
                return None
        else:
            return None

    def convert_dataframe(self, data, index, choice, post_fix):
        engine = self.DB.get_engine('db_zdt', 'qq')
        data_len = len(data)

        if choice == 1:
            for i in range(data_len):
                data[i][choice] = data[i][choice]

        df = pd.DataFrame(data, columns=index)

        # 今日涨停
        if choice == 1:
            self.today_zt(df, post_fix, engine)
        # 昨日涨停
        if choice == 2:
            self.yesterday_zt(df, post_fix, engine)

    # 今日涨停存储
    def today_zt(self, df, post_fix, engine):
        filename = os.path.join(
            self.path, self.today + "_" + post_fix + ".xls")

        df['今天的日期'] = self.today
        df.to_excel(filename, encoding='gbk')
        try:
            df.to_sql(self.today + post_fix, engine, if_exists='fail')
        except Exception as e:
            self.logger.info(e)

    # 昨日涨停今日的状态，今日涨停
    def yesterday_zt(self, df, post_fix, engine):
        df = df.set_index('序号')
        formula = lambda x: round(x * 100, 3)
        df['最大涨幅'] = df['最大涨幅'].map(formula)
        df['最大跌幅'] = df['最大跌幅'].map(formula)
        df['今日开盘涨幅'] = df['今日开盘涨幅'].map(formula)
        df['昨日涨停强度'] = df['昨日涨停强度'].map(lambda x: round(x, 0))
        df['今日涨停强度'] = df['今日涨停强度'].map(lambda x: round(x, 0))

        try:
            df.to_sql(self.today + post_fix, engine, if_exists='fail')
        except Exception as e:
            self.notify(f'{self.__class__} 出错')
            self.logger.info(e)

        title,content = self.generate_html(df)
        try:
            send_from_aliyun(title, content, types='html')
        except Exception as e:
            self.logger.error(e)

    def generate_html(self,df):
        avg = round(df['今日涨幅'].mean(), 2)
        median = round(df['今日涨幅'].median(), 2)
        min_v = round(df['今日涨幅'].min(), 2)
        min_index = df['今日涨幅'].argmin()
        min_percent_name = df.iloc[min_index]['名称']
        current = datetime.datetime.now().strftime('%Y-%m-%d')
        title = '昨涨停今天{}平均涨{}\n'.format(current, avg)
        content = '<p>昨天涨停今天<font color="red">{}</font></p>' \
                  '<p>平均涨幅 <font color="red">{}</font></p>' \
                  '<p>涨幅中位数 <font color="red">{}</font></p>' \
                  '<p>涨幅最小 <font color="red">{}</font></p>' \
                  '<p>涨幅最小股 <font color="red">{}</font></p>'.format(current, avg, median, min_v, min_percent_name)

        return title,content
    def start(self):
        zdt_content = self.download(self.zdt_url, headers=self.header_zdt)
        zdt_js = self.convert_json(zdt_content)
        self.convert_dataframe(zdt_js, self.zdt_indexx, 1, 'zdt')
        # 昨日涨停数据会如果不是当天获取会失效
        zrzt_content = self.download(self.zrzt_url, headers=self.header_zrzt)
        zrzt_js = self.convert_json(zrzt_content)
        self.convert_dataframe(zrzt_js, self.zrzt_indexx, 2, 'zrzt')


if __name__ == '__main__':
    obj = GetZDT()
    obj.start()
