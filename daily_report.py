# -*-coding=utf-8-*-
import datetime

__author__ = 'Rocky'
'''
http://30daydo.com
Email: weigesysu@qq.com
'''
from filter_stock import Filter_Stock
from setting import get_engine,sendmail
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
    zt_df[u'涨停强度']=map(lambda x:round(x,0),zt_df[u'涨停强度'])
    ret_df = zt_df[zt_df[u'代码'].isin(code_list)]
    if not ret_df.empty:
        tb_name_save = today+'_cx'
        excel_name = today+'_cx.xls'
        ret_df.to_excel(excel_name,encoding='gbk')
        ret_df.to_sql(tb_name_save,engine)
        s= ret_df[[u'代码',u'名称',u'涨停强度',u'打开次数',u'第一次涨停时间',u'最后一次涨停时间']].to_string()
        sendmail(s,today+u'次新涨停')

if __name__ == '__main__':
    main()