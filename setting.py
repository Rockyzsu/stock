# -*-coding=utf-8-*-
from toolkit import Toolkit
from sqlalchemy import create_engine
import redis
import MySQLdb
MYSQL_USER = Toolkit.getUserData('data.cfg')['MYSQL_USER']
MYSQL_PASSWORD = Toolkit.getUserData('data.cfg')['MYSQL_PASSWORD']
MYSQL_HOST = Toolkit.getUserData('data.cfg')['MYSQL_HOST']
MYSQL_PORT = Toolkit.getUserData('data.cfg')['MYSQL_PORT']
REDIS_HOST='localhost'
def get_engine(db):
    engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, db))
    return engine

def get_mysql_conn(db):
    conn = MySQLdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASSWORD,db,charset='utf8')
    return conn