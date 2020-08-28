# -*-coding=utf-8-*-

# @Time : 2020/2/27 14:05
# @File : realtme_jjjz.py
# 实时基金净值

import datetime
import json
import random
import re
import requests
import time

from settings import DBSelector, llogger
DB = DBSelector()

headers = {
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8',
}


def update_jj(table):
    # table='2020-02-25' # 用于获取code列
    conn = DB.get_mysql_conn('db_fund', 'qq')
    # today=datetime.datetime.now().strftime('%Y-%m-%d')
    logger = llogger(f'log/{table}_realtime.log')
    query = 'select `基金代码`,`基金简称`,`实时价格` from `{}`'.format(table)
    cursor = conn.cursor()
    cursor.execute(query)
    session = requests.Session()

    ret = cursor.fetchall()
    url = 'http://web.ifzq.gtimg.cn/fund/newfund/fundSsgz/getSsgz?app=web&symbol=jj{}&_var=LOAD_1582735233556_37'
    add_column1 = 'alter table `{}` add column `实时净值` float'.format(table)
    add_column2 = 'alter table `{}` add column `溢价率` float'.format(table)

    update_sql = 'update `{}` set `实时净值`= %s,`溢价率`=%s where  `基金代码`=%s'.format(table)

    try:
        cursor.execute(add_column1)
    except Exception as e:
        conn.rollback()
    else:
        conn.commit()

    try:
        cursor.execute(add_column2)
    except Exception as e:
        conn.rollback()
    else:
        conn.commit()

    for item in ret:

        code = item[0]
        realtime_price = item[2]
        s_resp = session.get(url.format(code), headers=headers)
        content = re.search('LOAD_\d+_\d+=(.*)', s_resp.text).group(1)
        js = json.loads(content)
        try:
            data_list = js.get('data').get('data')
        except Exception as e:
            logger.error(e)
            continue

        last_one = data_list[-1]
        time_ = last_one[0]

        jj_ = last_one[1]
        yjl = -1*round((jj_ - realtime_price) / realtime_price * 100, 2)
        print(f'溢价率-{yjl}')
        cursor.execute(update_sql, (jj_, yjl, code))
        conn.commit()
    logger.info('更新成功')
    conn.close()
