# -*-coding=utf-8-*-
from toolkit import Toolkit
from sqlalchemy import create_engine
import redis
import os
import MySQLdb
cfg_file=os.path.join(os.path.dirname(__file__),'data.cfg')
MYSQL_USER = Toolkit.getUserData(cfg_file)['MYSQL_USER']
MYSQL_PASSWORD = Toolkit.getUserData(cfg_file)['MYSQL_PASSWORD']
MYSQL_HOST = Toolkit.getUserData(cfg_file)['MYSQL_HOST']
MYSQL_PORT = Toolkit.getUserData(cfg_file)['MYSQL_PORT']
REDIS_HOST='localhost'
EMIAL_USER = Toolkit.getUserData(cfg_file)['EMAIL_USER']
EMIAL_PASS = Toolkit.getUserData(cfg_file)['EMAIL_PASSWORD']
SMTP_HOST = Toolkit.getUserData(cfg_file)['SMTP_HOST']
FROM_MAIL = Toolkit.getUserData(cfg_file)['FROM_MAIL']
TO_MAIL = Toolkit.getUserData(cfg_file)['TO_MAIL']

def get_engine(db):
    engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, db))
    return engine

def get_mysql_conn(db):
    conn = MySQLdb.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASSWORD,db,charset='utf8')
    return conn

