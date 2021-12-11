# -*-coding=utf-8-*-


__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
交割单处理 保存交割单到数据库
'''

import os
import datetime
import pandas as pd
import numpy as np
import re
from configure.settings import DBSelector
import fire

pd.set_option('display.max_rows', None)


class DeliveryOrder():

    def __init__(self):
        self.gj_table = 'tb_delivery_gj_django'
        self.hb_table = 'tb_delivery_hb_django'
        self.db_init()

    def db_init(self):
        DB = DBSelector()
        self.engine = DB.get_engine('db_stock', 'qq')
        self.conn = DB.get_mysql_conn('db_stock', 'qq')

    def setpath(self, path):
        path = os.path.join(os.getcwd(), path)
        if os.path.exists(path) == False:
            os.mkdir(path)
        os.chdir(path)

    # 单独处理华宝证券的数据
    def merge_data_HuaBao(self, filename):

        try:
            # 根据不同的格式选用不同的函数
            df = pd.read_csv(filename, encoding='gbk')
        except Exception as e:
            print(e)
            raise OSError("打开文件失败")

        df = df.reset_index(drop='True')
        df = df.dropna(subset=['成交时间'])

        df['成交日期'] = df['成交日期'].astype(np.str) + df['成交时间']

        # TODO 重复，删除
        df['成交日期'] = df['成交日期'].map(lambda x: datetime.datetime.strptime(
            x, "%Y%m%d%H:%M:%S").strftime('%Y-%m-%d %H:%M:%S'))
        try:

            df['成交日期'] = pd.to_datetime(df['成交日期'])
        except Exception as e:
            print(e)

        del df['股东代码']
        del df['成交时间']

        df = df[(df['委托类别'] == '买入') | (df['委托类别'] == '卖出')]
        df = df.fillna(0)
        df = df.sort_values(by='成交日期', ascending=False)
        cursor = self.conn.cursor()

        insert_cmd = f'''
               insert into {self.hb_table} (成交日期,证券代码,证券名称,委托类别,成交数量,成交价格,成交金额,发生金额,佣金,印花税,过户费,其他费) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        check_dup = f'''
               select * from {self.hb_table} where 成交日期=%s and 证券代码=%s and 委托类别=%s and 成交数量=%s and 发生金额=%s
               '''
        for index, row in df.iterrows():
            date = row['成交日期']
            date = date.to_pydatetime()
            cursor.execute(check_dup, (date, row['证券代码'], row['委托类别'], row['成交数量'], row['发生金额']))

            if cursor.fetchall():
                print('有重复数据，忽略')
                continue
            else:

                cursor.execute(insert_cmd, (
                    date, row['证券代码'], row['证券名称'], row['委托类别'], row['成交数量'], row['成交价格'], row['成交金额'], row['发生金额'],
                    row['佣金'], row['印花税'], row['过户费'], row['其他费']))

        self.conn.commit()
        self.conn.close()

    # 合并一年的交割单
    def years_ht(self):
        df_list = []
        for i in range(1, 2):
            # 固定一个文件
            filename = 'HT_2018-05_week4-5.xls'
            try:
                t = pd.read_table(filename, encoding='gbk',
                                  dtype={'证券代码': np.str})
            except Exception as e:
                print(e)
                continue
            df_list.append(t)
        df = pd.concat(df_list)
        df = df.reset_index()
        df['成交日期'] = map(lambda x: datetime.datetime.strptime(
            str(x), "%Y%m%d"), df['成交日期'])
        df = df[df['摘要'] != '申购配号']
        df = df[df['摘要'] != '质押回购拆出']
        df = df[df['摘要'] != '拆出质押购回']
        del df['合同编号']
        del df['备注']
        del df['股东帐户']
        del df['结算汇率']

        del df['Unnamed: 16']
        df = df.sort_values(by='成交日期')
        df = df.set_index('成交日期')

        df.to_sql('tb_delivery_HT', self.engine, if_exists='append')

    def caculation(self, df):
        fee = df['手续费'].sum() + df['印花税'].sum() + df['其他杂费'].sum()
        print(fee)

    # 计算每个月的费用

    def month(self):
        pass

    # 国金账户 2018-01 到 11月数据入库， 这个函数不用动了。保留csv格式
    def years_gj(self):
        df_list = []
        for i in range(2, 12):
            filename = 'GJ_2018_%s.csv' % str(i).zfill(2)
            try:
                t = pd.read_csv(filename, encoding='gbk', dtype={'证券代码': np.str})
            except Exception as e:
                print(e)
            df_list.append(t)
        df = pd.concat(df_list)
        df = df.reset_index(drop='True')

        df['成交日期'] = df['成交日期'].astype(np.str) + df['成交时间']

        df['成交日期'] = df['成交日期'].map(lambda x: datetime.datetime.strptime(
            x, "%Y%m%d%H:%M:%S").strftime('%Y-%m-%d %H:%M:%S'))
        try:

            df['成交日期'] = pd.to_datetime(df['成交日期'])
        except Exception as e:
            print(e)

        del df['股东帐户']
        del df['成交时间']

        df = df.sort_values(by='成交日期', ascending=False)
        df = df.set_index('成交日期')

        df.to_sql('tb_delivery_gj', self.engine, if_exists='replace')

    def file_exists(self, filepath):
        return True if os.path.exists(filepath) else False

    # 单独处理某个文件（单独一个月的数据） 文件格式：国金-保存为xls，然后另存为csv 或者按照天也可以
    def years_gj_each_month_day(self, filename):
        if not self.file_exists(filename):
            raise ValueError('路径不存在')

        try:
            # 根据不同的格式选用不同的函数
            df = pd.read_csv(filename, encoding='gbk', dtype={'证券代码': np.str})
        except Exception as e:
            print(e)
            raise ValueError('读取文件错误')

        df = df.reset_index(drop='True')

        df['成交日期'] = df['成交日期'].astype(np.str) + df['成交时间']

        df['成交日期'] = df['成交日期'].map(lambda x: datetime.datetime.strptime(
            x, "%Y%m%d%H:%M:%S").strftime('%Y-%m-%d %H:%M:%S'))
        try:

            df['成交日期'] = pd.to_datetime(df['成交日期'])
        except Exception as e:
            print(e)

        del df['股东帐户']
        del df['成交时间']

        df = df.fillna(0)
        df = df[(df['操作'] != '申购配号') & (df['操作'] != '拆出质押购回') & (df['操作'] != '质押回购拆出')]
        df = df.sort_values(by='成交日期', ascending=False)
        cursor = self.conn.cursor()
        insert_cmd = f'''
        insert into {self.gj_table} (成交日期,证券代码,证券名称,操作,成交数量,成交均价,成交金额,余额,发生金额,手续费,印花税,过户费,本次金额,其他费用,交易市场) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        check_dup = f'''
        select * from {self.gj_table} where 成交日期=%s and 证券代码=%s and 操作=%s and 成交数量=%s and 余额=%s
        '''
        for index, row in df.iterrows():
            date = row['成交日期']
            date = date.to_pydatetime()
            cursor.execute(check_dup, (date, row['证券代码'], row['操作'], row['成交数量'], row['余额']))
            if cursor.fetchall():
                print('有重复数据，忽略')

            else:
                cursor.execute(insert_cmd, (
                    date, row['证券代码'], row['证券名称'], row['操作'], row['成交数量'], row['成交均价'], row['成交金额'], row['余额'],
                    row['发生金额'], row['手续费'], row['印花税'], row['过户费'], row['本次金额'], row['其他费用'], row['交易市场']))

        self.conn.commit()
        self.conn.close()

    def pretty(self):
        df = pd.read_sql('tb_delivery_GJ', self.engine, index_col='成交日期')
        # print(df)
        # del df['Unnamed: 17']
        del df['index']
        df.to_sql('tb_delivery_GJ', self.engine, if_exists='replace')

    # 数据同步到另一个django数据库
    def data_sync(self):
        cursor = self.conn.cursor()
        # 最新的数据库
        select_cmd = '''select * from tb_delivery_gj'''
        cursor.execute(select_cmd)
        ret = list(cursor.fetchall())
        print('new db ', len(ret))
        # 旧的数据库
        select_cmd2 = '''select * from tb_delivery_gj_django'''
        cursor.execute(select_cmd2)
        ret2 = list(cursor.fetchall())
        print('old db ', len(ret2))
        ret_copy = ret.copy()

        for item in ret:
            # print(item)
            for item2 in ret2:
                if item[0] == item2[0] and item[1] == item2[1] and item[2] == item2[2] and item[4] == item2[4] and item[
                    5] == item2[5]:
                    try:
                        ret_copy.remove(item)
                    except Exception as e:
                        continue
        for i in ret_copy:
            update_sql = '''
            insert into tb_delivery_gj_django (成交日期,证券代码,证券名称,操作,成交数量,成交均价,成交金额,)
            '''

        print('diff len ', len(ret_copy))

    # 银转证
    def bank_account(self):
        folder_path = os.path.join(os.path.dirname(__file__), 'private')
        os.chdir(folder_path)

        df_list = []
        for file in os.listdir(folder_path):
            if re.search('2', file.decode('gbk')):
                df = pd.read_table(file, encoding='gbk')
                df_list.append(df)

        total_df = pd.concat(df_list)
        del total_df['货币单位']
        del total_df['合同编号']
        del total_df['Unnamed: 8']
        del total_df['银行名称']

        total_df['发生金额'] = map(lambda x, y: x * -1 if y ==
                                                      '证券转银行' else x, total_df['发生金额'], total_df['操作'])

        total_df['委托时间'] = map(lambda x: str(x).zfill(6), total_df['委托时间'])

        total_df['日期'] = map(lambda x, y: str(x) + " " + y,
                             total_df['日期'], total_df['委托时间'])
        total_df['日期'] = pd.to_datetime(total_df['日期'], format='%Y%m%d %H%M%S')
        total_df = total_df.set_index('日期')

        df = total_df[total_df['备注'] == '成功[[0000]交易成功]']
        del df['备注']
        del df['委托时间']
        df.to_sql('tb_bank_cash', self.engine, if_exists='replace')


def GJfunc(obj, path, name):
    # path = base_path + broker
    obj.setpath(path)
    # obj.data_sync()
    obj.years_gj_each_month_day(filename=name)
    # obj.years_gj_each_month()
    # obj.years_gj()
    # obj.years_ht()
    # bank_account()
    # obj.pretty()


def HBfunc(obj, path, name):
    obj.setpath(path)
    obj.merge_data_HuaBao(filename=name)


def main(broker, name):
    '''
    broker: HB GJ
    name
    '''
    # 国金
    obj = DeliveryOrder()
    base_path = f'private/{datetime.date.today().year}/'
    path = base_path + broker

    # 国金
    if broker == 'GJ':
        GJfunc(obj, path, name)

    # 华宝
    elif broker == 'HB':
        HBfunc(obj, path, name)


if __name__ == '__main__':
    fire.Fire(main)
