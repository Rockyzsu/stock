# -*-coding=utf-8-*-

from setting import get_mysql_conn
import os

db_name = 'db_stock'

conn = get_mysql_conn(db_name,local=False)

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
        cmd = '''INSERT INTO `tb_blacklist` (CODE,NAME,REASON) VALUES (\"%s\",\"%s\",\"%s\")''' % (code, name, reason)
        try:
            cur.execute(cmd)
            conn.commit()
        except Exception, e:
            print e
            conn.rollback()


def main():
    filename = os.path.join(os.path.dirname(__file__), 'data', 'blacklist.csv')
    create_tb()
    update_data(filename)


# validation()

if __name__ == '__main__':
    main()
