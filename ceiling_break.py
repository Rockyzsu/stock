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

# 推送股价信息到手机
class break_monitor():
    def __init__(self):
        cfg = Toolkit.getUserData('data.cfg')
        from_mail = cfg['from_mail']
        password = cfg['password']
        to_mail = cfg['to_mail']
        smtp_server = 'smtp.qq.com'

        self.server = smtp_server
        self.username = from_mail.split("@")[0]
        self.from_mail = from_mail
        self.password = password
        self.to_mail = to_mail
        self.bases = pd.read_csv('bases.csv', dtype={'code': np.str})
        self.stocklist = Toolkit.read_stock('monitor_list.log')
        # 初始化邮箱设置读取需要股票信息
        # 这样子只登陆一次
        try:
            self.smtp = smtplib.SMTP_SSL(port=465)
            self.smtp.connect(self.server)
            self.smtp.login(self.username, self.password)
        except smtplib.SMTPException, e:
            print e
            return 0

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

    #开板提示
    def break_ceil(self, code):
        print "E"
        print threading.current_thread().name
        while 1:
            #print code
            time.sleep(2)
            try:
                df = ts.get_realtime_quotes(code)
            except:
                time.sleep(5)
                continue
            v = long(df['b1_v'].values[0])
            print datetime.datetime.now().strftime("%H:%M:%S")
            print v
            #print type(v)
            if v <= 1000:
                print u"小于万手，小心！跑"

                self.push_msg('break', 10, 10, 'down')
                #这里可以优化，不必每次都登陆。


    def monitor_break(self):
        print "C"
        thread_num = len(self.stocklist)
        thread_list = []
        join_list = []
        for i in range(thread_num):
            print "D"
            t = threading.Thread(target=self.break_ceil, args=(i,))
            thread_list.append(t)
        #print "FFFFF"
        #print thread_list

        for j in thread_list:
            print "GGGGG"
            j.start()
            #j.join()


if __name__ == '__main__':
    print "A"
    path = os.path.join(os.getcwd(), 'data')
    if os.path.exists(path) == False:
        os.mkdir(path)
    os.chdir(path)
    obj = break_monitor()
    print 'B'
    obj.monitor_break()
