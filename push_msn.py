# -*-coding=utf-8-*-
__author__ = 'Rocky'
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from toolkit import Toolkit
from email.mime.multipart import MIMEMultipart
from email import Encoders, Utils
from toolkit import Toolkit
import tushare as ts
#推送股价信息到手机
class MailSend():
    def __init__(self, smtp_server, from_mail, password, to_mail):
        self.server = smtp_server
        self.username = from_mail.split("@")[0]
        self.from_mail = from_mail
        self.password = password
        self.to_mail = to_mail

        # 初始化邮箱设置

    def send_txt(self, name,price,percent):
        content='%s higher than %.2f, %.2f' %(name,price,percent)
        content=content+'%'
        print content
        subject='%s' %name
        self.msg=MIMEText(content,'plain','utf-8')
        self.msg['to'] = self.to_mail
        self.msg['from'] = self.from_mail
        self.msg['Subject'] = subject
        self.msg['Date'] = Utils.formatdate(localtime=1)
        try:

            self.smtp = smtplib.SMTP_SSL(port=465)
            self.smtp.connect(self.server)
            self.smtp.login(self.username, self.password)
            self.smtp.sendmail(self.msg['from'], self.msg['to'], self.msg.as_string())
            self.smtp.quit()
            print "sent"
        except smtplib.SMTPException,e:
            print e
            return 0

def push_msg(name,price,percent):
    cfg=Toolkit.getUserData('data.cfg')
    from_mail=cfg['from_mail']
    password=cfg['password']
    to_mail=cfg['to_mail']
    obj=MailSend('smtp.qq.com',from_mail,password,to_mail)
    obj.send_txt(name,price,percent)

def read_stock():
    f=open('stock.txt')
    stock_list=[]

    for s in f.readlines():
        s= s.strip()
        row=s.split(';')
        #print row
        #print "code :",row[0]
        #rint "price :",row[1]
        stock_list.append(row)

    return stock_list

def meet_price(code,price):
    df=ts.get_realtime_quotes(code)
    real_price= df['price'].values[0]
    name=df['name'].values[0]
    real_price=float(real_price)
    pre_close=float(df['pre_close'].values[0])
    percent=(real_price-pre_close)/pre_close*100
    print percent
    #percent=df['']
    #print type(real_price)
    if real_price>=price:
        print '%s price higher than %.2f%percent, %.2f' %(name,price,percent),
        print '%'
        push_msg(name,price,percent)

def main():
    #read_stock()
    stock_lists=read_stock()
    while 1:
        for each_stock in stock_lists:
            code=each_stock[0]
            price=float(each_stock[1])
            meet_price(code,price)
    #meet_price('300333',14.1)


if __name__=='__main__':
    main()