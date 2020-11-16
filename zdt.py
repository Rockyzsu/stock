# -*- coding=utf-8 -*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
# 每天的涨跌停
import re
import time
import xlwt
import os
from settings import DATA_PATH
import pandas as pd
from settings import DBSelector, send_from_aliyun
import requests
import datetime
from BaseService import BaseService


class GetZDT(BaseService):

    def __init__(self, today=None, logpath='log/zdt.log'):
        '''
        TODAY 格式 20200701
        :param today:
        '''
        super(GetZDT, self).__init__(logpath)

        if today:
            self.today = today
        else:
            self.today = time.strftime("%Y%m%d")

        self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36"

        self.path = DATA_PATH

        self.zdt_url = 'http://home.flashdata2.jrj.com.cn/limitStatistic/ztForce/' + \
                       self.today + ".js"
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

    def getdata(self, url, headers, retry=5):

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
                self.notify(title='获取涨跌停数据出错', desp=f'{self.__class__}')
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
                self.notify(title='获取涨跌停数据出错', desp=f'{self.__class__}')
                self.logger.info(e)
                return None
        else:
            return None


    def save_to_dataframe(self, data, index, choice, post_fix):
        engine = self.DB.get_engine('db_zdt', 'qq')
        data_len = len(data)
        filename = os.path.join(
            self.path, self.today + "_" + post_fix + ".xls")

        if choice == 1:
            for i in range(data_len):
                data[i][choice] = data[i][choice]

        df = pd.DataFrame(data, columns=index)


        # 今日涨停
        if choice == 1:
            df['今天的日期'] = self.today
            df.to_excel(filename, encoding='gbk')
            try:
                df.to_sql(self.today + post_fix, engine, if_exists='fail')
            except Exception as e:
                self.logger.info(e)

        # 昨日涨停
        if choice == 2:
            df = df.set_index('序号')
            formula = lambda x: round(x * 100, 3)
            df['最大涨幅'] = df['最大涨幅'].map(formula)
            df['最大跌幅'] =    df['最大跌幅'].map(formula)
            df['今日开盘涨幅'] = df['今日开盘涨幅'].map(formula)
            df['昨日涨停强度'] = df['昨日涨停强度'].map(lambda x: round(x, 0))
            df['今日涨停强度'] = df['今日涨停强度'].map(lambda x: round(x, 0))
            try:
                df.to_sql(self.today + post_fix, engine, if_exists='fail')
            except Exception as e:
                self.notify(f'{self.__class__} 出错')
                self.logger.info(e)

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
                      '<p>涨幅最小股 <font color="red">{}</font></p>'.format(current, avg, median, min_v,min_percent_name)

            try:
                send_from_aliyun(title, content, types='html')
            except Exception as e:
                print(e)

    # 昨日涨停今日的状态，今日涨停

    def storedata(self):
        zdt_content = self.getdata(self.zdt_url, headers=self.header_zdt)
        zdt_js = self.convert_json(zdt_content)
        self.save_to_dataframe(zdt_js, self.zdt_indexx, 1, 'zdt')

        # 昨日涨停数据会如果不是当天获取会失效
        zrzt_content = self.getdata(self.zrzt_url, headers=self.header_zrzt)

        zrzt_js = self.convert_json(zrzt_content)
        self.save_to_dataframe(zrzt_js, self.zrzt_indexx, 2, 'zrzt')


if __name__ == '__main__':
    # 填补以前的数据
    # date_list = [i for i in list(pd.date_range('20180921','20190101'))]
    # conn = get_mysql_conn('db_zdt','local')
    # cursor = conn.cursor()
    # for d in date_list:
    #     x=datetime.datetime.strftime(d, '%Y%m%d')
    #     y=datetime.datetime.strftime(d, '%Y-%m-%d')
    #     if ts.is_holiday(y):
    #         continue
    #     print(y)
    #     check_cmd ='select 1 from `{}zdt`'.format(x)
    #     try:
    #         cursor.execute(check_cmd)
    #     except Exception as e:
    #         print(e)
    #         obj = GetZDT(x)
    #         obj.storedata()
    #     else:
    #         ret = cursor.fetchone()
    #         print(ret)
    #         continue

    obj = GetZDT()
    obj.storedata()
