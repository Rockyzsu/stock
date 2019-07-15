# -*-coding=utf-8-*-

# @Time : 2019/7/12 18:41
# @File : transfer_data_es.py

from setting import get_mysql_conn
from elasticsearch import Elasticsearch

es = Elasticsearch('10.18.6.102:9200')
conn = get_mysql_conn('db_stock','local')
cursor = conn.cursor()

query_cmd = 'select * from tb_cnstock'
cursor.execute(query_cmd)

ret = cursor.fetchall()

for item in ret:
    # print(item)
    date = item[0]
    title = item[1]
    url = item[2]
    content = item[3]
    keyword = item[4]
    body = {'Title':title,'ULR':url,'keyword':keyword,'content':content,'Date':date}
    try:
        es.index(index='cnstock',doc_type='doc',body=body)
    except Exception as e:
        print(e)
        print(url)
