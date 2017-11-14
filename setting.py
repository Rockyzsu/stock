# -*-coding=utf-8-*-
from toolkit import Toolkit
from sqlalchemy import create_engine

USER = Toolkit.getUserData('data.cfg')['MYSQL_USER']
PASSWORD = Toolkit.getUserData('data.cfg')['MYSQL_PASSWORD']
HOST = Toolkit.getUserData('data.cfg')['MYSQL_HOST']
PORT = Toolkit.getUserData('data.cfg')['MYSQL_PORT']
DB = 'stock'
engine = create_engine('mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(USER, PASSWORD, HOST, PORT, DB))
