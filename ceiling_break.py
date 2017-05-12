__author__ = 'vmplay'
#监测开板信号

# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
import smtplib, time,os,datetime
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

# 推送股价信息到手机
class break_monitor():
    def __init__(self):
        cfg = Toolkit.getUserData('data.cfg')
        from_mail = cfg['from_mail']
        password = cfg['password']
        to_mail = cfg['to_mail']
        smtp_server='smtp.qq.com'

        self.server = smtp_server
        self.username = from_mail.split("@")[0]
        self.from_mail = from_mail
        self.password = password
        self.to_mail = to_mail
        self.bases=pd.read_csv('bases.csv',dtype={'code':np.str})
        self.stocklist=Toolkit.read_stock('monitor_list.log')
        # 初始化邮箱设置读取需要股票信息
        #这样子只登陆一次
        try:
            self.smtp = smtplib.SMTP_SSL(port=465)
            self.smtp.connect(self.server)
            self.smtp.login(self.username, self.password)
        except smtplib.SMTPException, e:
            print e
            return 0

    #格式需要修改
    def send_txt(self, name, content):

        content = content + '%'

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


    def push_msg(self,name, price, percent, status):
        cfg = Toolkit.getUserData('data.cfg')
        from_mail = cfg['from_mail']
        password = cfg['password']
        to_mail = cfg['to_mail']
        #obj = MailSend('smtp.qq.com', from_mail, password, to_mail)
        self.send_txt(name, price, percent, status)



    #开板提示
    def break_ceil(self,code):
        while 1:
            time.sleep(2)
            try:
                df=ts.get_realtime_quotes(code)
            except:
                time.sleep(5)
                continue
            v=long(df['b1_v'].values[0])
            print datetime.datetime.now().strftime("%H:%M:%S")
            print v
            #print type(v)
            if  v<=10000 :
                print u"小于万手，小心！跑"

                self.push_msg('break',10,10,'down')
                #这里可以优化，不必每次都登陆。



    def monitor_break(self):
        #all_base=pd.read_csv('bases.csv',dtype={'code':np.str})
        break_ceil('002868')

#读入要监测的stock list 多线程运行
def main():
    # read_stock()
    choice = input("Input your choice:\n")



if __name__ == '__main__':
    path=os.path.join(os.getcwd(),'data')
    if os.path.exists(path)==False:
        os.mkdir(path)
    os.chdir(path)
    obj=break_monitor()
    obj.monitor_break()
