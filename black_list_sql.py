#-*-coding=utf-8-*-

import MySQLdb
import setting

db_name = 'db_stcok'

conn = MySQLdb.connect( host = setting.MYSQL_REMOTE,
						port =3306,
                       user=setting.MYSQL_REMOTE_USER,
                       passwd=setting.MYSQL_PASSWORD,
                       db=db_name,
                       charset='utf8'
						)

cur = conn.cursor()

def create_tb():
	cmd = '''CREATE TABLE IF NOT EXISTS `tb_blacklist` ( DATA DATATIME,);'''