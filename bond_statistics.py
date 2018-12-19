# -*-coding=utf-8-*-
import datetime

import pymongo
from send_mail import sender_139

__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
from scipy import stats
import tushare as ts
from setting import get_engine
import pandas as pd
from filter_stock import Filter_Stock


# 筛选出 新股 的可转债
current = datetime.datetime.now()
last_week = current + datetime.timedelta(days=7*-2)
conn = get_engine('db_stock')
df = pd.read_sql('tb_bond_jisilu', con=conn)
code_list = df['正股代码'].values
kzz_code_list = df['可转债代码'].values
kzz_name_list = df['可转债名称'].values
db=pymongo.MongoClient('10.18.6.26',port=27001)

# 获取次新股的可转债数据
def get_zhenggu():
    obj = Filter_Stock()
    ns_df = obj.get_new_stock('2016','2018')
    zg_code = ns_df[ns_df['code'].isin(code_list)]['code'].values

    ret_df = df[df['正股代码'].isin(zg_code)]
    ret_df=ret_df.reset_index(drop=True)
    ret_df.to_sql('tb_new_stock_bond',con=conn,if_exists='replace')

# 筛选出每周 （月）涨幅排名倒数的10个
def sort_top_raise(count=10,ktype='W',reverse=True):
    p_list = [get_percentage(code, ktype) for code in kzz_code_list]
    kzz_dict = dict(zip(kzz_name_list,p_list))

    # 去重未上市的
    kzz_dict_copy = kzz_dict.copy()
    for k,v in kzz_dict_copy.items():
        if v==-999:
            del kzz_dict[k]

    top_raise_list = sorted(kzz_dict.items(),key=lambda x:x[1],reverse=True)
    return top_raise_list

def get_percentage(code,ktype):
    last_week_str = last_week.strftime('%Y-%m-%d')
    count=0
    retry=5
    # 重试5次
    while 1:
        try:
            df = ts.get_k_data(code,ktype=ktype,start=last_week_str)
        except Exception as e:
            print(e)
            count+=1
            print('retry >> {}'.format(count))
            if count==retry:
                df=pd.DataFrame()
                break
            else:
                continue
        else:
            break

    # 未上市
    if len(df)==0:
        percentage=-999
    else:
        weeks_close = df['close'].values

        if len(weeks_close)==2:
            percentage = round((weeks_close[1]-weeks_close[0])/weeks_close[0]*100,2)
        else:
            percentage=-999

    return percentage

# 将list保存为mongo
def save_list_mongo(source_list):
    current=datetime.datetime.now()
    title=current.strftime('%Y-%m-%d')+'可转债周涨幅的前10和后10'
    top10=source_list[:10]
    last10=source_list[-10:]
    top_str = ['{} : {}'.format(i[0],i[1])for i in top10]
    last_str = ['{} : {}'.format(i[0],i[1])for i in last10[::-1]]
    top_str='\n'.join(top_str)
    last_str='\n'.join(last_str)
    content = '跌幅前10:::\n'+last_str+'\n涨幅前10:::\n'+top_str
    try:
        sender_139(title,content)
    except Exception as e:
        print(e)

    d=dict(source_list)
    d['updated']=current

    try:
        db['db_parker']['kzz_weekly_raise'].insert(d)
    except Exception as e:
        print(e)


if __name__=="__main__":
    source_list=sort_top_raise()
    save_list_mongo(source_list)