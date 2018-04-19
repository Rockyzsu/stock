# -*-coding=utf-8-*-
import datetime
import re

__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
from setting import get_engine,get_mysql_conn
import pandas as pd

def clone_database():
    local_db =get_mysql_conn('db_zdt',local=True)
    cur = local_db.cursor()
    cur.execute('show tables')
    tables=cur.fetchall()
    local_engine = get_engine('db_zdt',local=True)
    dfs=[]
    for table in tables:

        try:
            result =re.findall('(\d+)zdt$', table[0])
            if result:
                print table[0]
                current = result[0]
                # d= datetime.datetime.strptime(current,'%Y%m%d').strftime('%Y-%m-%d')
                # print d
                df =pd.read_sql(table[0],local_engine,index_col='index')
                # df[u'涨停日期']=d
                df=df.rename(columns={u'最后一次涨停时间A':u'最后一次涨停时间',u'第一次涨停时间A':u'第一次涨停时间'})
                try:
                    print df.head()
                    df.to_sql(table[0],local_engine,if_exists='replace')
                except Exception,e:
                    print e

        except Exception,e:
            print e
            print table[0]
        # dfs.append(pd.read_sql(table[0],local_engine))
    # df= pd.concat(dfs)
    # print df.head()
def merge_database():
    local_db =get_mysql_conn('db_zdt',local=True)
    cur = local_db.cursor()
    cur.execute('show tables')
    tables=cur.fetchall()
    local_engine = get_engine('db_zdt',local=True)
    dfs=[]
    for table in tables:
        try:
            result =re.findall('(\d+)zdt$', table[0])
            if len(result)>0:
                print table[0]
                df =pd.read_sql(table[0],local_engine,index_col='index')
                dfs.append(df)

        except Exception,e:
            print e
            print table[0]
    dfx= pd.concat(dfs)
    print dfx.head()

    # ali_engine = get_engine(None,local=False)
    local_engine_stock=get_engine('db_stock',local=True)
    dfx.to_sql('tb_zdt',local_engine_stock,if_exists='replace')


if __name__=="__main__":
    # clone_database()
    merge_database()
