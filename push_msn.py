# -*-coding=utf-8-*-
__author__ = 'Rocky'
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from toolkit import Toolkit
from email.mime.multipart import MIMEMultipart
from email import Encoders, Utils
from toolkit import Toolkit
#推送股价信息到手机
class MailSend():
    def __init__(self, smtp_server, from_mail, password, to_mail):
        self.server = smtp_server
        self.username = from_mail.split("@")[0]
        self.from_mail = from_mail
        self.password = password
        self.to_mail = to_mail

        # 初始化邮箱设置

    def send_txt(self, subject,content):
        # 这里发送附件尤其要注意字符编码，当时调试了挺久的，因为收到的文件总是乱码

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
        except smtplib.SMTPException,e:
            print e
            return 0

def push_msg():
    cfg=Toolkit('cfg')
    from_mail=cfg['from_mail']
    password=cfg['password']
    to_mail=cfg['to_mail']
    obj=MailSend('smtp.qq.com',from_mail,password,to_mail)
