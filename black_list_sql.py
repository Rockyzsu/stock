# -*-coding=utf-8-*-

import MySQLdb
import setting
import os

db_name = 'db_stock'

conn = MySQLdb.connect(host=setting.MYSQL_REMOTE,
                       port=3306,
                       user=setting.MYSQL_REMOTE_USER,
                       passwd=setting.MYSQL_PASSWORD,
                       db=db_name,
                       charset='utf8'
                       )

cur = conn.cursor()


def create_tb():
    cmd = '''CREATE TABLE IF NOT EXISTS `tb_blacklist` (DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,CODE VARCHAR(6) PRIMARY KEY,NAME VARCHAR(60),REASON TEXT);'''
    try:
        cur.execute(cmd)
        conn.commit()
    except Exception, e:
        print e
        conn.rollback()


# conn.close()

def update_data(filename):
    with open(filename, 'r') as f:
        content = f.readlines()
    if not content:
        exit()

    for line in content:
        (code, name, reason) = line.strip().split(';')
        print code
        # cmd = '''INSERT INTO `tb_blacklist` (CODE,NAME,REASON) VALUES (\"%s\",\"%s\",\"%s\")''' % (code, name, reason)
        # print cmd
        # try:
        #     cur.execute(cmd)
        #     conn.commit()
        # except Exception, e:
        #     print e
        #     conn.rollback()


from setting import get_engine

engine = get_engine('db_stock')
import pandas as pd

base = pd.read_sql('bases', engine, index_col='index')


def validation():
    cmd = 'select `CODE` from tb_blacklist'
    cur.execute(cmd)
    result = cur.fetchall()
    for each in result:
        # print each[0]
        print base[base['code'] == each[0]]['name'].values[0], '\t',
        print base[base['code'] == each[0]]['area'].values[0]


def main():
    filename = os.path.join(os.path.dirname(__file__), 'data', 'blacklist.csv')
    create_tb()
    update_data(filename)


# validation()

if __name__ == '__main__':
    main()
