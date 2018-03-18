# -*- coding=utf-8 -*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
# 每天的涨跌停
# url=http://stock.jrj.com.cn/tzzs/zdtwdj/zdforce.shtml
import urllib2, re, time, xlrd, xlwt, sys, os
import setting
import pandas as pd

reload(sys)
sys.setdefaultencoding('gbk')


class GetZDT():
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.today = time.strftime("%Y%m%d")
        # self.today="20180313"
        self.path = os.path.join(os.path.dirname(__file__), 'data')

        self.zdt_url = 'http://home.flashdata2.jrj.com.cn/limitStatistic/ztForce/' + self.today + ".js"
        self.zrzt_url = 'http://hqdata.jrj.com.cn/zrztjrbx/limitup.js'

        self.host = "home.flashdata2.jrj.com.cn"
        self.reference = "http://stock.jrj.com.cn/tzzs/zdtwdj/zdforce.shtml"

        self.header_zdt = {"User-Agent": self.user_agent,
                           "Host": self.host,
                           "Referer": self.reference}

        self.zdt_indexx = [u'代码', u'名称', u'最新价格', u'涨跌幅', u'封成比', u'封流比', u'封单金额', u'第一次涨停时间', u'最后一次涨停时间', u'打开次数',
                           u'振幅',
                           u'涨停强度']

        self.zrzt_indexx = [u'序号', u'代码', u'名称', u'昨日涨停时间', u'最新价格', u'今日涨幅', u'最大涨幅', u'最大跌幅', u'是否连板', u'连续涨停次数',
                            u'昨日涨停强度', u'今日涨停强度'
            , u'是否停牌', u'昨天的日期', u'昨日涨停价', u'今日开盘价格', u'今日开盘涨幅']

        self.header_zrzt = {"User-Agent": self.user_agent,
                            "Host": "hqdata.jrj.com.cn",
                            "Referer": "http://stock.jrj.com.cn/tzzs/zrztjrbx.shtml"
                            }

    def getData(self, url, headers, retry=5):
        req = urllib2.Request(url=url, headers=headers)
        for _ in range(retry):
            try:
                resp = urllib2.urlopen(req)
                content = resp.read()
                if content:
                    return content
                else:
                    time.sleep(60)
                    continue
            except Exception, e:
                time.sleep(60)
                continue

    def convert_json(self, content):
        p = re.compile(r'"Data":(.*)};', re.S)
        result = p.findall(content)
        if result:
            t1 = result[0]
            t2 = list(eval(t1))
            return t2
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
        ws.write(0, 0, u'代码')
        ws.write(0, 1, u'名称')
        ws.write(0, 2, u'最新价格')
        ws.write(0, 3, u'涨跌幅')
        ws.write(0, 4, u'封成比')
        ws.write(0, 5, u'封流比')
        ws.write(0, 6, u'封单金额')
        ws.write(0, 7, u'第一次涨停时间')
        ws.write(0, 8, u'最后一次涨停时间')
        ws.write(0, 9, u'打开次数')
        ws.write(0, 10, u'振幅')
        ws.write(0, 11, u'涨停强度')
        print "Rows:%d" % rows
        for row in data:
            rows = len(data)
            cols = len(row)
            point_y = 0
            for col in row:
                # print col
                # table.put_cell(row,col,)
                print col
                ws.write(point_x, point_y, col)
                print "[%d,%d]" % (point_x, point_y)
                point_y = point_y + 1

            point_x = point_x + 1

        w.save(excel_filename)

    def save_to_dataframe(self, data, indexx, choice, post_fix):
        engine = setting.get_engine('db_zdt')
        l = len(data)
        if choice==1:
            for i in range(l):
                data[i][choice] = data[i][choice].decode('gbk')

        df = pd.DataFrame(data, columns=indexx)
        if choice==2:
            df=df.set_index(u'序号')
        filename = os.path.join(self.path, self.today + "_" + post_fix + ".xls")
        if choice == 1:
            df.to_excel(filename, encoding='gbk')

        df.to_sql(self.today + post_fix, engine, if_exists='replace')

    # 昨日涨停今日的状态，今日涨停
    def storeData(self):
        zdt_content = self.getData(self.zdt_url, headers=self.header_zdt)
        zdt_js = self.convert_json(zdt_content)
        self.save_to_dataframe(zdt_js, self.zdt_indexx, 1, 'zdt')

        zrzt_content = self.getData(self.zrzt_url, headers=self.header_zrzt)
        zrzt_js = self.convert_json(zrzt_content)
        self.save_to_dataframe(zrzt_js, self.zrzt_indexx, 2, 'zrzt')


if __name__ == '__main__':
    obj = GetZDT()
    obj.storeData()
