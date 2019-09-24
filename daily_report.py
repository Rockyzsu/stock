# -*-coding=utf-8-*-
import datetime

__author__ = 'Rocky'
'''
http://30daydo.com
Email: weigesysu@qq.com
'''
from filter_stock import Filter_Stock
from settings import get_engine,sendmail
import pandas as pd


def main():
    obj = Filter_Stock()
    now =datetime.datetime.now()
    today = now.strftime("%Y%m%d")
    tb_name = today+'zdt'
    end = str(now.year)+'-'+str(now.month - 1)

    df = obj.get_new_stock('2015',end)
    code_list =df['code'].values
    engine = get_engine('db_zdt')
    zt_df = pd.read_sql(tb_name,engine,index_col='index')
    zt_df['涨停强度']=map(lambda x:round(x,0),zt_df['涨停强度'])
    ret_df = zt_df[zt_df['代码'].isin(code_list)]
    if not ret_df.empty:
        tb_name_save = today+'_cx'
        excel_name = today+'_cx.xls'
        ret_df.to_excel(excel_name,encoding='gbk')
        ret_df.to_sql(tb_name_save,engine)
        s= ret_df[['代码','名称','涨停强度','打开次数','第一次涨停时间','最后一次涨停时间']].to_string()
        sendmail(s,today+'次新涨停')

if __name__ == '__main__':
    main()