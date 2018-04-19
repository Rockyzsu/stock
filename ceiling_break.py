# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
import smtplib, time, os, datetime
from email.mime.text import MIMEText
from email.header import Header
from toolkit import Toolkit
from email.mime.multipart import MIMEMultipart
from email import Encoders, Utils
from toolkit import Toolkit
import tushare as ts
from pandas import Series
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import threading
from setting import  get_engine,sendmail
# from setting import MsgSend
# msg = MsgSend(u'wei')

EXCEPTION_TIME_OUT = 60
NORMAL_TIME_OUT = 3
TIME_RESET = 60 * 5


# 监测涨停板开板监测
class BreakMonitor():
    def __init__(self, send=True):
        self.send = send
        engine = get_engine('db_stock')
        self.bases = pd.read_sql('tb_basic_info', engine, index_col='index')
        # self.stocklist = Toolkit.read_stock('monitor_list.log')

    # 格式需要修改
    def send_txt(self, name, content):
        subject = '%s' % name
        self.msg = MIMEText(content, 'plain', 'utf-8')
        self.msg['to'] = self.to_mail
        self.msg['from'] = self.from_mail
        self.msg['Subject'] = subject
        self.msg['Date'] = Utils.formatdate(localtime=1)
        try:
            self.smtp.sendmail(self.msg['from'], self.msg['to'], self.msg.as_string())
            self.smtp.quit()
            print "sent"
        except smtplib.SMTPException, e:
            print e
            return 0

    # 开板提示
    def break_ceil(self, code):
        print threading.current_thread().name
        while 1:
            # print code
            time.sleep(2)
            try:
                df = ts.get_realtime_quotes(code)
            except:
                time.sleep(5)
                continue
            v = long(df['b1_v'].values[0])

            if v <= 1000:
                print datetime.datetime.now().strftime("%H:%M:%S")
                print u"小于万手，小心！跑"
                print self.bases[self.bases['code'] == code]['name'].values[0]
                if self.send == True:
                    self.push_msg('break', 10, 10, 'down')
                # 这里可以优化，不必每次都登陆。s

    def monitor_break(self, send=True):
        thread_num = len(self.stocklist)
        thread_list = []
        join_list = []
        for i in range(thread_num):
            t = threading.Thread(target=self.break_ceil, args=(self.stocklist[i],))
            thread_list.append(t)

        for j in thread_list:
            j.start()

        for k in thread_list:
            k.join()


def break_monitor(code, warning_vol):
    start = True
    start_monitor = True
    waiting_time = datetime.datetime.now()
    conn = ts.get_apis()
    while 1:
        current = datetime.datetime.now()
        try:
            if start_monitor:
                try:
                    df = ts.quotes(code, conn=conn)
                except Exception,e:
                    print e
                    time.sleep(EXCEPTION_TIME_OUT)
                    conn = ts.get_apis()
                    continue
                print 'under monitor {}'.format(current)

            if df['bid_vol1'].values[0] < warning_vol and start:
                title=code+' Buy +1 : '+str(df['bid_vol1'].values[0])
                sendmail(title,title)
                # msg.send_ceiling(code, df['bid_vol1'].values[0])
                start = False
                start_monitor = False
                waiting_time = current + datetime.timedelta(seconds=TIME_RESET)
            time.sleep(NORMAL_TIME_OUT)
        except Exception, e:
            print e
            time.sleep(EXCEPTION_TIME_OUT)
            conn = ts.get_apis()
            continue
        if current > waiting_time:
            start = True
            start_monitor = True


if __name__ == '__main__':
    path = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)
    # obj = break_monitor(send=False)
    # obj.monitor_brea k()
    break_monitor('000977', 2000)
    # ts.close_apis(conn=conn)
