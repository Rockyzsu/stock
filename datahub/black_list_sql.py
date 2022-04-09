# -*-coding=utf-8-*-
# 股市黑名单
import sys

sys.path.append('..')
from configure.settings import DBSelector, config
import os
import codecs
from loguru import logger

logger = logger.add('log/blacklist.log')
DATA_PATH = config.get('data_path')


def create_tb(conn):
    cmd = '''CREATE TABLE IF NOT EXISTS `tb_blacklist` (DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,CODE VARCHAR(6) PRIMARY KEY,NAME VARCHAR(60),REASON TEXT);'''
    cur = conn.cursor()

    try:
        cur.execute(cmd)
    except Exception as e:
        logger.info(e)
        conn.rollback()
    else:
        conn.commit()


def update_data(filename, conn):
    cur = conn.cursor()

    with codecs.open(filename, 'r', encoding='utf8') as f:
        content = f.readlines()
    if not content:
        return

    for line in content:
        (code, name, reason) = line.strip().split(';')
        cmd = '''INSERT INTO `tb_blacklist` (CODE,NAME,REASON) VALUES (\"%s\",\"%s\",\"%s\")''' % (code, name, reason)

        try:
            cur.execute(cmd)

        except Exception as e:
            logger.info(e)
            logger.info('dup code {}'.format(code))
            conn.rollback()
            continue
        else:
            conn.commit()
            logger.info('insert successfully {}'.format(name))


# 调试
def get_name_number():
    filename = os.path.join(DATA_PATH, 'blacklist.csv')

    with codecs.open(filename, 'r', encoding='utf8') as f:
        content = f.readlines()
    if not content:
        return
    logger.info('len of content {}'.format(len(content)))
    code_list = []
    for i in content:
        code_list.append(i.split(';')[0])
    logger.info(code_list)
    logger.info(len(set(code_list)))

    # 找出重复

    seen = set()
    dup_list = []
    for i in code_list:
        if i in seen:
            dup_list.append(i)
        else:
            seen.add(i)
    logger.info('dup item {}'.format(dup_list))


def main():
    filename = os.path.join(DATA_PATH, 'blacklist.csv')
    # 本地更新
    db_name = 'db_stock'
    DB = DBSelector()
    conn = DB.get_mysql_conn(db_name, 'qq')
    create_tb(conn)
    update_data(filename, conn)

    # 远程更新
    # db_name = 'db_stock'
    remote_conn = DB.get_mysql_conn('qdm225205669_db', 'qq')
    create_tb(remote_conn)
    update_data(filename, remote_conn)


if __name__ == '__main__':
    main()
    # get_name_number()
