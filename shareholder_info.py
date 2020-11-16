# -*- coding: utf-8 -*-
# @Time : 2019/1/19 14:37
# @File : stockholder_info.py
# 股东信息获取
import pandas as pd
import time

import pymysql
import tushare as ts
import config
from configure.settings import get_mysql_conn

conn = get_mysql_conn('db_stock', 'local')
cursor = conn.cursor()

token = config.token

ts.set_token(token)

pro = ts.pro_api()


def get_stock_list():
    df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    return dict(zip(list(df['ts_code'].values), list(df['name'].values)))


# 生产日期 2000到2018
def create_date():
    start_date = '20{}0101'
    end_date = '20{}1231'
    date_list = []
    for i in range(18, 0, -1):
        print(start_date.format(str(i).zfill(2)))
        print(end_date.format(str(i).zfill(2)))
        date_list.append(i)
    return date_list


# 十大和十大流通
def get_stockholder(code, start, end):
    # 十大非流通
    global pro
    try:
        stockholder = pro.top10_holders(ts_code=code, start_date=start, end_date=end)
        time.sleep(1)
        stockfloat = pro.top10_floatholders(ts_code=code, start_date=start, end_date=end)
        time.sleep(1)

    except Exception as e:
        print(e)
        time.sleep(10)
        ts.set_token(token)
        pro = ts.pro_api()

    else:
        if stockholder.empty and stockfloat.empty:
            return pd.DataFrame(), pd.DataFrame()

        else:
            return stockholder, stockfloat


# 十大 股东 流动
def insert_db(df, name, float_holder=True):
    if float_holder:
        insert_cmd = '''
        insert into tb_sharesholder (code,name,ann_date,end_date,holder_name,hold_amount,hold_ratio)VALUES (%s,%s,%s,%s,%s,%s,%s)'''

        for index, row in df.iterrows():
            # print(index, row['ts_code'], row['ann_date'], row['end_date'], row['holder_name'], row['hold_amount'],
            #       row['hold_ratio'])
            try:
                cursor.execute(insert_cmd, (
                    row['ts_code'].split('.')[0], name, row['ann_date'], row['end_date'], row['holder_name'],
                    row['hold_amount'], row['hold_ratio']))

            except pymysql.err.IntegrityError:
                print('dup item')
                conn.rollback()
                continue
            else:
                conn.commit()


    else:
        insert_cmd = '''
        insert into tb_sharesholder_float (code,name,ann_date,end_date,holder_name,hold_amount)VALUES (%s,%s,%s,%s,%s,%s)'''

        for index, row in df.iterrows():
            # print(index, row['ts_code'], row['ann_date'], row['end_date'], row['holder_name'], row['hold_amount'])
            try:
                cursor.execute(insert_cmd, (
                    row['ts_code'].split('.')[0], name, row['ann_date'], row['end_date'], row['holder_name'],
                    row['hold_amount']))
            except pymysql.err.IntegrityError:

                print('dup')
                conn.rollback()
                continue
            else:
                conn.commit()

    conn.commit()
    print('save successful')


def main():
    code_dict = get_stock_list()
    next_stock = True
    check_sql = '''
    SELECT code FROM `tb_sharesholder_float` GROUP BY code'''

    cursor.execute(check_sql)
    ret = cursor.fetchall()
    result = []
    for i in ret:
        result.append(i[0])

    for code, name in code_dict.items():
        # if next_stock:
        print('name ：', name)
        temp_code = code.split('.')[0]
        if temp_code in result:
            continue

        start_date = '20{}0101'
        end_date = '20{}1231'
        for i in range(18, 0, -1):
            start = start_date.format(str(i).zfill(2))
            end = end_date.format(str(i).zfill(2))
            df0, df1 = get_stockholder(code, start, end)
            if not df0.empty and not df1.empty:
                insert_db(df0, name, True)
                insert_db(df1, name, False)
            else:
                # 换一个个股
                # next_stock=False
                break


def test():
    # 过了时间还是有数据
    code = '603259.SH'
    start = '2010-01-01'
    end = '2012-02-02'
    stockholder = pro.top10_holders(ts_code=code, start_date=start, end_date=end)
    print(stockholder)


# test()
# create_date()
# df0, df1 = get_stockholder('300333.SZ', '20180101', '20181231')
# insert_db(df0)
main()
conn.close()
