# -*-coding=utf-8-*-
# 股市黑名单
from setting import get_mysql_conn,llogger,DATA_PATH
import os

db_name = 'db_stock'

conn = get_mysql_conn(db_name,local=False)

cur = conn.cursor()

logger = llogger(__file__)

def create_tb():
    cmd = '''CREATE TABLE IF NOT EXISTS `tb_blacklist` (DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,CODE VARCHAR(6) PRIMARY KEY,NAME VARCHAR(60),REASON TEXT);'''
    try:
        cur.execute(cmd)
        conn.commit()
    except Exception as e:
        logger.info(e)
        conn.rollback()


def update_data(filename):
    with open(filename, 'r') as f:
        content = f.readlines()
    if not content:
        return

    for line in content:
        (code, name, reason) = line.strip().split(';')
        cmd = '''INSERT INTO `tb_blacklist` (CODE,NAME,REASON) VALUES (\"%s\",\"%s\",\"%s\")''' % (code, name, reason)
        cur.execute(cmd)

        try:
            conn.commit()
        except Exception as e:
            logger.info(e)
            conn.rollback()


def main():
    filename = os.path.join(DATA_PATH, 'blacklist.csv')
    create_tb()
    update_data(filename)

if __name__ == '__main__':
    main()
