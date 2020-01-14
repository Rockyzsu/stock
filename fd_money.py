# @Time : 2020/1/14 0:05
# @File : fd_money.py
# 涨停封单数据
from settings import get_mysql_conn
import datetime
import tushare as ts
import matplotlib.pyplot as plt

conn = get_mysql_conn('db_zdt', 'local')
cursor = conn.cursor()
diff_day = 20
dataset=[]
date=[]
for d in range(diff_day):
    day = datetime.datetime.now() + datetime.timedelta(days=-1 * d)
    # if ts.is_holiday(day.strftime('%Y-%m-%d')):
    #     continue

    sql = 'select 封单金额 as total_money from `{}zdt`'.format(day.strftime('%Y%m%d'))

    # sql = '''select sum(封单金额) as total_money from `20200113zdt`'''
    # print(sql)
    try:
        cursor.execute(sql)
        ret = cursor.fetchone()
        # print(ret[0])
        dataset.append(int(ret[0]/10000))
        date.append(day.strftime('%Y%m%d'))
    except Exception as e:
        pass

dataset_ = dataset[::-1]
date_ = date[::-1]
print(dict(zip(date_,dataset_)))
plt.plot(date_,dataset_)
plt.show()
input()
