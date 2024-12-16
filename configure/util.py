# -*- coding: utf-8 -*-
# @Time : 2020/11/16 11:37
# @File : util.py
# @Author : Rocky C@www.30daydo.com

import datetime
import random
import smtplib
import time
import warnings
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr
import json
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr
import email
from email.mime.multipart import MIMEMultipart
import pandas as pd
import re
import requests
from .settings import config, get_config_data,DBSelector
import datetime

def notify(title='', desp=''):
    warnings.warn("该接口需要收费了，请使用企业微信")
    url = f"https://sc.ftqq.com/{config['WECHAT_ID']}.send?text={title}&desp={desp}"
    try:
        res = requests.get(url, timeout=5)
    except Exception as e:
        print(e)
        return False

    else:
        try:
            js = res.json()
            result = True if js['data']['errno'] == 0 else False
            if result:
                print('发送成功')
                return True
            else:
                print('发送失败')
                return False

        except Exception as e:
            print(e)
            print(res.text)


def read_web_headers_cookies(website, headers=False, cookies=False):
    config = get_config_data('web_headers.json')
    return_headers = None
    return_cookies = None

    if headers:
        return_headers = config[website]['headers']

    if cookies:
        return_headers = config[website]['cookies']

    return return_headers, return_cookies


def send_message_via_wechat(_message):  # 默认发送给自己
    _config = config['enterprise_wechat']
    userid = _config['userid']
    agentid = _config['agentid']
    corpid = _config['corpid']
    corpsecret = _config['corpsecret']

    response = requests.get(f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corpid}&corpsecret={corpsecret}")
    data = json.loads(response.text)
    access_token = data['access_token']

    json_dict = {
        "touser": userid,
        "msgtype": "text",
        "agentid": agentid,
        "text": {
            "content": _message
        },
        "safe": 0,
        "enable_id_trans": 0,
        "enable_duplicate_check": 0,
        "duplicate_check_interval": 1800
    }
    json_str = json.dumps(json_dict)
    response_send = requests.post(f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}",
                                  data=json_str)
    return json.loads(response_send.text)['errmsg'] == 'ok'


def rsa_encrypt():
    import rsa
    (pubkey, privkey) = rsa.newkeys(1024)
    print('pubkey >>>> {}'.format(pubkey))
    print('privkey >>>> {}'.format(privkey))

    with open('pub.pem', 'w') as f:
        f.write(pubkey.save_pkcs1().decode())

    with open('datasender.pem', 'w') as f:
        f.write(privkey.save_pkcs1().decode())

    message = ''
    print("message encode {}".format(message.encode()))
    crypto = rsa.encrypt(message.encode(), pubkey)  # 加密数据为bytes

    print('密文:\n{}'.format(crypto))

    with open('encrypt.bin', 'wb') as f:
        f.write(crypto)
    # 解密
    e_message = rsa.decrypt(crypto, privkey)  # 解密数据也是为bytes
    print("解密后\n{}".format(e_message.decode()))


def rsa_decrypt():
    import rsa
    with open('encrypt.bin', 'rb') as f:
        content = f.read()

    file = 'priva.pem'
    with open(file, 'r') as f:
        privkey = rsa.PrivateKey.load_pkcs1(f.read().encode())

    e_message = rsa.decrypt(content, privkey)  # 解密数据也是为bytes
    print("解密后\n{}".format(e_message.decode()))


def market_status():
    '''
    收盘
    '''
    now = datetime.datetime.now()
    end = datetime.datetime(now.year, now.month, now.day, 15, 2, 5)
    return True if now < end else False


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def send_from_aliyun(title, content, TO_MAIL_=config['mail']['qq']['user'], types='plain'):
    username = config['aliyun']['EMAIL_USER_ALI']  # 阿里云
    password = config['aliyun']['LOGIN_EMAIL_ALYI_PASSWORD']  # 阿里云
    stmp = smtplib.SMTP()

    msg = MIMEText(content, types, 'utf-8')
    subject = title
    msg['Subject'] = Header(subject, 'utf-8')
    msg['From'] = _format_addr('{} <{}>'.format('数据推送', username))
    msg['To'] = TO_MAIL_

    try:
        stmp.connect('smtp.qiye.aliyun.com', 25)
        stmp.login(username, password)
        stmp.sendmail(username, TO_MAIL_, msg.as_string())
    except Exception as e:
        time.sleep(10 + random.randint(1, 5))
        stmp = smtplib.SMTP()
        stmp.connect('smtp.qiye.aliyun.com', 25)
        stmp.login(username, password)
        stmp.sendmail(username, TO_MAIL_, msg.as_string())
    else:
        print('发送完毕')


def send_sms(content):
    '''
    一个海外的短信接口
    '''
    from twilio.rest import Client

    client = Client(config.twilio_account_sid, config.twilio_auth_token)
    try:
        message = client.messages.create(
            body=content,
            from_=config.FROM_MOBILE,
            to=config.TO_MOBILE
        )
    except Exception as e:
        print(e)



def jsonp2json(str_):
    return json.loads(str_[str_.find('{'):str_.rfind('}') + 1])

def js2json(str_):
    import demjson
    return demjson.decode(str_[str_.find('{'):str_.rfind('}') + 1])

def bond_filter(code):
    m = re.search('^(11|12)', code)
    return True if m else False


def get_holding_list(filename=None):
    '''
    获取持仓列表
    '''
    df = pd.read_csv(filename, encoding='gbk')
    df['证券代码'] = df['证券代码'].astype(str)
    df['kzz'] = df['证券代码'].map(bond_filter)
    df = df[df['kzz'] == True]
    return df['证券代码'].tolist()

def mongo_convert_df(doc,condition=None,project=None):
    import pandas as pd
    result =[]
    for item in doc.find(condition,project):
        result.append(item)
    return pd.DataFrame(result)

def get_jsl_code(table):
    # from settings import DBSelector
    engine = DBSelector().get_engine('db_stock','kh')
    df = pd.read_sql(table,engine)
    return df

def fmt_date(x,src='%Y%m%d',trgt='%Y-%m-%d'):
    return datetime.datetime.strptime(x, src).strftime(trgt)


def calendar(start_date,end_date):
    from .settings import get_tushare_pro

    src='%Y-%m-%d'
    trgt='%Y%m%d'
    start_date = fmt_date(start_date,src,trgt)
    end_date = fmt_date(end_date,src,trgt)

    pro = get_tushare_pro()
    df = pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date, is_open='1')

    cal = df['trade_date'].tolist()
    cal = list(map(fmt_date, cal))

    return cal

def send_from_aliyun_ssl(title,content,TO_MAIL_=config['mail']['qq']['user'],types='plain'):


    '''~~~smtp认证使用的邮箱账号密码~~~'''
    username = config['aliyun']['EMAIL_USER_ALI']  # 阿里云
    password = config['aliyun']['LOGIN_EMAIL_ALYI_PASSWORD']  # 阿里云

    '''~~~定义发件地址~~~'''
    From = formataddr([username,username])  #昵称(邮箱没有设置外发指定自定义昵称时有效)+发信地址(或代发)
    replyto = username  #回信地址

    '''定义收件对象'''
    to = ','.join([TO_MAIL_, TO_MAIL_])  #收件人
    rcptto = [to]  #完整的收件对象

    '''定义主题'''
    Subject = title

    '''~~~开始构建message~~~'''
    msg = MIMEMultipart('alternative')
    '''1.1 收发件地址、回信地址、Message-id、发信时间、邮件主题'''
    msg['From'] = From
    msg['Reply-to'] = replyto
    msg['TO'] = to
    # msg['Cc'] = cc
    # msg['Bcc'] = bcc  #建议密送地址在邮件头中隐藏
    msg['Message-id'] = email.utils.make_msgid()
    msg['Date'] = email.utils.formatdate()
    msg['Subject'] = Subject
    ''''1.2 正文text/plain部分'''
    textplain = MIMEText(content, _subtype=types, _charset='UTF-8')
    msg.attach(textplain)
    '''1.3 封装附件'''
    # file = r'C:\Users\yourname\Desktop\某文件夹\123.pdf'   #指定本地文件，请换成自己实际需要的文件全路径。
    # att = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
    # att["Content-Type"] = 'application/octet-stream'
    # att.add_header("Content-Disposition", "attachment", filename='123.pdf')
    # msg.attach(att)

    '''~~~开始连接验证服务~~~'''
    try:
        client = smtplib.SMTP_SSL('smtp.qiye.aliyun.com', 465)
        print('smtp_ssl----连接服务器成功，现在开始检查账号密码')
    except Exception as e1:
        client = smtplib.SMTP('smtp.qiye.aliyun.com', 25, timeout=5) 
        print('smtp----连接服务器成功，现在开始检查账号密码')
    except Exception as e2:
        print('抱歉，连接服务超时')
        return

    try:
        client.login(username, password)
        print('账密验证成功')
    except:
        print('抱歉，账密验证失败')
        return

    '''~~~发送邮件并结束任务~~~'''
    client.sendmail(username, (','.join(rcptto)).split(','), msg.as_string())
    client.quit()


def is_weekday_today():
    # 获取当前日期
    today = datetime.date.today()

    # 获取星期几（0代表星期一，6代表星期日）
    weekday = today.weekday()

    # 判断是否为工作日（星期一到星期五）
    if weekday < 5:
        return True
    else:
        return False



if __name__ == '__main__':
    print(get_jsl_code('tb_bond_jisilu'))

