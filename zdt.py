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
from settings import is_holiday, DATA_PATH
import pandas as pd
from settings import llogger,DBSelector,send_from_aliyun
import requests
import datetime

logger = llogger('log/zdt.log')

class GetZDT(object):

    def __init__(self,today):
        '''
        TODAY 格式 20200701
        :param today:
        '''
        self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/64.0.3282.167 Chrome/64.0.3282.167 Safari/537.36"

        if today is None:
            self.today = time.strftime("%Y%m%d")
        else:
            self.today = today

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
                    logger.info('failed to get content, retry: {}'.format(i))
                    continue
            except Exception as e:
                sender_139('获取涨跌停数据出错','{}'.format(e))
                logger.error(e)
                time.sleep(60)
                continue
        return None

    def convert_json(self, content):
        p = re.compile(r'"Data":(.*)};', re.S)
        if len(content) <= 0:
            logger.info('Content\'s length is 0')
            exit(0)
        result = p.findall(content)
        if result:
            try:
                # print(result)
                t1 = result[0]
                t2=re.sub('[\\r\\n]', '', t1)
                t2=re.sub(',,',',0,0',t2)
                t2 = re.sub('Infinity','-1',t2)
                t2 = re.sub('NaN','-1',t2)
                t2 = list(eval(t2))
                return t2
            except Exception as e:
                sender_139('获取涨跌停数据出错','e{}'.format(e))
                logger.info(e)
                return None
        else:
            return None

    # 2016-12-27 to do this
    def save_excel(self, date, data):
        # data is list type
        w = xlwt.Workbook(encoding='gbk')
        ws = w.add_sheet(date)
        excel_filename = date + ".xls"
        # sheet=open_workbook(excel_filenme)
        # table=wb.sheets()[0]
        xf = 0
        ctype = 1
        rows = len(data)
        point_x = 1
        point_y = 0
        ws.write(0, 0, '代码')
        ws.write(0, 1, '名称')
        ws.write(0, 2, '最新价格')
        ws.write(0, 3, '涨跌幅')
        ws.write(0, 4, '封成比')
        ws.write(0, 5, '封流比')
        ws.write(0, 6, '封单金额')
        ws.write(0, 7, '第一次涨停时间')
        ws.write(0, 8, '最后一次涨停时间')
        ws.write(0, 9, '打开次数')
        ws.write(0, 10, '振幅')
        ws.write(0, 11, '涨停强度')
        print("Rows:%d" % rows)
        for row in data:
            rows = len(data)
            cols = len(row)
            point_y = 0
            for col in row:
                # print(col)
                # table.put_cell(row,col,)
                # print(col)
                ws.write(point_x, point_y, col)
                # print("[%d,%d]" % (point_x, point_y))
                point_y = point_y + 1

            point_x = point_x + 1

        w.save(excel_filename)

    def save_to_dataframe(self, data, indexx, choice, post_fix):
        engine = self.DB.get_engine('db_zdt','qq')
        if not data:
            exit()
        data_len = len(data)
        if choice == 1:
            for i in range(data_len):
                data[i][choice] = data[i][choice]

        df = pd.DataFrame(data, columns=indexx)

        filename = os.path.join(
            self.path, self.today + "_" + post_fix + ".xls")

        # 今日涨停
        if choice == 1:
            df['今天的日期'] = self.today
            df.to_excel(filename, encoding='gbk')
            try:
                df.to_sql(self.today + post_fix, engine, if_exists='fail')
            except Exception as e:
                logger.info(e)
        # 昨日涨停
        if choice == 2:
            df = df.set_index('序号')
            df['最大涨幅'] = df['最大涨幅'].map(lambda x: round(x * 100, 3))
            df['最大跌幅'] = df['最大跌幅'].map(lambda x: round(x * 100, 3))
            df['今日开盘涨幅'] = df['今日开盘涨幅'].map(lambda x: round(x * 100, 3))
            df['昨日涨停强度'] = df['昨日涨停强度'].map(lambda x: round(x, 0))
            df['今日涨停强度'] = df['今日涨停强度'].map(lambda x: round(x, 0))
            try:
                df.to_sql(self.today + post_fix, engine, if_exists='fail')
            except Exception as e:
                logger.info(e)

            avg = round(df['今日涨幅'].mean(), 2)
            median = round(df['今日涨幅'].median(), 2)
            min_v = round(df['今日涨幅'].min(), 2)

            current = datetime.datetime.now().strftime('%Y-%m-%d')
            title = '昨涨停今天{}平均涨{}\n'.format(current, avg)
            content = '<p>昨天涨停今天<font color="red">{}</font></p>' \
                      '<p>平均涨幅 <font color="red">{}</font></p>' \
                      '<p>涨幅中位数 <font color="red">{}</font></p>' \
                      '<p>涨幅最小 <font color="red">{}</font></p>'.format(current,avg,median,min_v)

            try:
                send_from_aliyun(title, content,types='html')
            except Exception as e:
                print(e)

    # 昨日涨停今日的状态，今日涨停

    def storedata(self):
        zdt_content = self.getdata(self.zdt_url, headers=self.header_zdt)
        # logger.info('zdt Content' + zdt_content)
        zdt_js = self.convert_json(zdt_content)
        self.save_to_dataframe(zdt_js, self.zdt_indexx, 1, 'zdt')

        # 昨日涨停数据会如果不是当天获取会失效
        time.sleep(0.5)
        zrzt_content = self.getdata(self.zrzt_url, headers=self.header_zrzt)
        logger.info('zrzt Content' + zrzt_content)

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

    check = True

    if check and is_holiday():
        logger.info('Holiday')
        exit()

    logger.info("start")
    obj = GetZDT(None)
    obj.storedata()
