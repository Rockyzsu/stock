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

#监测涨停板开板监测
class break_monitor():
    def __init__(self,send=True):
        self.send=send
        if self.send==True:
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
            # 初始化邮箱设置读取需要股票信息
            # 这样子只登陆一次
            try:
                self.smtp = smtplib.SMTP_SSL(port=465)
                self.smtp.connect(self.server)
                self.smtp.login(self.username, self.password)
            except smtplib.SMTPException, e:
                print e
                return 0
        self.bases = pd.read_csv('bases.csv', dtype={'code': np.str})
        self.stocklist = Toolkit.read_stock('monitor_list.log')


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

            if v <= 1000:
                print datetime.datetime.now().strftime("%H:%M:%S")
                print u"小于万手，小心！跑"
                print self.bases[self.bases['code']==code]['name'].values[0]
                if self.send==True:
                    self.push_msg('break', 10, 10, 'down')
                #这里可以优化，不必每次都登陆。s


    def monitor_break(self,send=True):
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


if __name__ == '__main__':
    path = os.path.join(os.getcwd(), 'data')
    if os.path.exists(path) == False:
        os.mkdir(path)
    os.chdir(path)
    obj = break_monitor(send=False)
    obj.monitor_break()
