# -*-coding=utf-8-*-
__author__ = 'Rocky'
import smtplib, time
from email.mime.text import MIMEText
from email.header import Header
from toolkit import Toolkit
from email.mime.multipart import MIMEMultipart
from email import Encoders, Utils
from toolkit import Toolkit
import tushare as ts
from pandas import Series
import matplotlib.pyplot as plt


# 推送股价信息到手机
class MailSend():
    def __init__(self, smtp_server, from_mail, password, to_mail):
        self.server = smtp_server
        self.username = from_mail.split("@")[0]
        self.from_mail = from_mail
        self.password = password
        self.to_mail = to_mail

        # 初始化邮箱设置

    def send_txt(self, name, price, percent, status):
        if 'up' == status:
            content = '%s > %.2f , %.2f' % (name, price, percent)
        if 'down' == status:
            content = '%s < %.2f , %.2f' % (name, price, percent)

        content = content + '%'
        print content
        subject = '%s' % name
        self.msg = MIMEText(content, 'plain', 'utf-8')
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
        except smtplib.SMTPException, e:
            print e
            return 0


def push_msg(name, price, percent, status):
    cfg = Toolkit.getUserData('data.cfg')
    from_mail = cfg['from_mail']
    password = cfg['password']
    to_mail = cfg['to_mail']
    obj = MailSend('smtp.qq.com', from_mail, password, to_mail)
    obj.send_txt(name, price, percent, status)


def read_stock(name):
    f = open(name)
    stock_list = []

    for s in f.readlines():
        s = s.strip()
        row = s.split(';')
        # print row
        # print "code :",row[0]
        # rint "price :",row[1]
        stock_list.append(row)

    return stock_list


def meet_price(code, price_up, price_down):
    try:
        df = ts.get_realtime_quotes(code)
    except Exception, e:
        print e
        time.sleep(5)
        return 0
    real_price = df['price'].values[0]
    name = df['name'].values[0]
    real_price = float(real_price)
    pre_close = float(df['pre_close'].values[0])
    percent = (real_price - pre_close) / pre_close * 100
    # print percent
    # percent=df['']
    # print type(real_price)
    if real_price >= price_up:
        print '%s price higher than %.2f , %.2f' % (name, real_price, percent),
        print '%'
        push_msg(name, real_price, percent, 'up')
        return 1
    if real_price <= price_down:
        print '%s price lower than %.2f , %.2f' % (name, real_price, percent),
        print '%'
        push_msg(name, real_price, percent, 'down')
        return 1


def meet_percent(code, percent_up, percent_down):
    try:
        df = ts.get_realtime_quotes(code)
    except Exception, e:
        print e
        time.sleep(5)
        return 0
    real_price = df['price'].values[0]
    name = df['name'].values[0]
    real_price = float(real_price)
    pre_close = float(df['pre_close'].values[0])
    real_percent = (real_price - pre_close) / pre_close * 100
    # print percent
    # percent=df['']
    # print type(real_price)
    if real_percent >= percent_up:
        print '%s percent higher than %.2f , %.2f' % (name, real_percent, real_price),

        push_msg(name, real_price, real_price, 'up')
        return 1
    if real_percent <= percent_down:
        print '%s percent lower than %.2f , %.2f' % (name, real_percent, real_price),
        print '%'
        push_msg(name, real_price, real_percent, 'down')

        return 1


# 推送一般的实盘消息
def general_info():
    t_all = ts.get_today_all()
    result = []
    t1 = t_all[t_all['changepercent'] <= -9.0].count()['changepercent']
    result.append(t1)
    for i in range(-9, 9, 1):
        temp = t_all[(i * 1.00 < t_all['changepercent']) & (t_all['changepercent'] <= (i + 1) * 1.00)].count()[
            'changepercent']
        result.append(temp)
    t2 = t_all[t_all['changepercent'] > 9.0].count()['changepercent']
    result.append(t2)
    return result


def visual():
    data = general_info()
    s = Series(data=data, index=[range(-10, 10)])

    print s
    fg = s.plot(kind='bar', table=True)
    plt.show(fg)


def main():
    # read_stock()
    choice = input("Input your choice:\n")

    if str(choice) == '1':
        # using price:
        stock_lists_price = read_stock('price.txt')
        while 1:
            t = 0
            for each_stock in stock_lists_price:
                code = each_stock[0]
                price_down = float(each_stock[1])
                price_up = float(each_stock[2])
                t = meet_price(code, price_up, price_down)
                if t:
                    stock_lists_price.remove(each_stock)

    if str(choice) == '2':
        # using percent
        stock_lists_percent = read_stock('percent.txt')
        while 1:
            t = 0
            for each_stock in stock_lists_percent:
                code = each_stock[0]
                percent_down = float(each_stock[1])
                percent_up = float(each_stock[2])
                t = meet_percent(code, percent_up, percent_down)
                if t:
                    stock_lists_percent.remove(each_stock)


if __name__ == '__main__':
    # main()
    # general_info()
    visual()
