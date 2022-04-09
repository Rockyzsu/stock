# -*-coding=utf-8-*-

'''
__author__ = 'Rocky'
http://30daydo.com
Email: weigesysu@qq.com
每日涨停报告
'''

import datetime
import fire
import pandas as pd
import sys

sys.path.append('..')
from configure.settings import DBSelector
from configure.util import send_from_aliyun
from filterstock import FilterStock


def get_zt_info(obj, now):
    '''
    数据库获取新股的涨停信息
    '''
    today_str = now.strftime('%Y%m%d')
    tb_name = today_str + 'zdt'
    end = str(now.year) + '-' + str(now.month).zfill(2)
    start = '2015-01'
    df = obj.get_new_stock(start, end)
    code_list = df['code'].values
    engine = DBSelector().get_engine('db_zdt')
    zt_df = pd.read_sql(tb_name, engine, index_col='index')
    zt_df['涨停强度'] = zt_df['涨停强度'].map(lambda x: round(x, 0))
    ret_df = zt_df[zt_df['代码'].isin(code_list)]
    s = ""

    if not ret_df.empty:
        s = ret_df[['代码', '名称', '涨停强度', '打开次数', '第一次涨停时间', '最后一次涨停时间']].to_string()

    save_local = False  # 保存在本地
    if save_local:
        excel_name = today_str + '_次新.xls'
        ret_df.to_excel(excel_name, encoding='gbk')

        #
        # tb_name_save = today_str + '_cx'
        # ret_df.to_sql(tb_name_save, engine)

    return s


def send_zt_report(today=None):
    if today is None:
        now = datetime.datetime.now().strftime("%Y%m%d")

    else:
        now = datetime.datetime.strptime(str(today), '%Y%m%d')

    obj = FilterStock()
    info = get_zt_info(obj, now)
    send_from_aliyun(str(today) + '次新涨停', info)


if __name__ == '__main__':
    fire.Fire(send_zt_report)
