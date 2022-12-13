# -*-coding=utf-8-*-
'''
__author__ = 'Rocky'
email: weigesysu@qq.com
'''
import datetime
import tushare as ts
import os
import pandas as pd
from collections import OrderedDict
import matplotlib
import numpy as np
import matplotlib.pyplot as plt

import sys
sys.path.append('..')
from configure.settings import DBSelector

matplotlib.use("Pdf")
pd.set_option('display.max_rows', None)


# 过滤器，剔除不想要的个股

class FilterStock():

    def __init__(self):

        self.change_work_dir()
        self.today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.engine = DBSelector().get_engine('db_stock')
        self.conn = DBSelector().get_engine('db_stock')

    def change_work_dir(self):
        current = os.path.dirname(__file__)
        work_space = os.path.join(current, 'data')
        if os.path.exists(work_space) == False:
            os.mkdir(work_space)

        os.chdir(work_space)

    def get_location(self):
        df = ts.get_area_classified()
        print(df)
        # df.to_excel('location.xls')
        self.save_to_excel(df, 'location.xls')

    def get_ST(self):
        # 暂停上市
        zt = ts.get_suspended()
        print(zt)
        # 终止上市
        zz = ts.get_terminated()
        print(zz)

    def get_achievement(self):
        fc = ts.forecast_data(2016, 4)
        print(fc)

    def daily_market(self):
        '''
        保存每天收盘后的市场行情
        :return:
        '''
        df = ts.get_today_all()
        print(df)
        try:
            df.to_sql(self.today, self.engine, if_exists='replace')
        except Exception as e:
            print(e)
        print("Save {} data to MySQL".format(self.today))

    def break_low(self, date):
        '''
        筛选出一年内创新低的股票
        :param date: 某一天的日期 ‘'2017-11-11
        :return:
        '''
        # cmd = 'select * from `{}`'.format(date)
        df = pd.read_sql_table(date, self.engine, index_col='index')
        # **** 这里的index需要删除一个
        low_db = self.conn('db_selection')
        low_cursor = low_db.cursor()
        for i in range(len(df)):
            code = df.loc[i]['code']
            cur_low = df.loc[i]['low']

            mins_date, mins = self.get_lowest(code, '2017', date)
            if not mins_date:
                continue
            if mins and float(cur_low) <= float(mins) and float(cur_low) != 0.0:
                print(code, )
                print(df.loc[i]['name'])
                print('year mins {} at {}'.format(mins, mins_date))
                print('curent mins ', cur_low)
                create_cmd = 'create table if not exists break_low' \
                             '(`index` int primary key auto_increment,datetime datetime,code text,name text,low_price float,last_price float, last_price_date datetime);'
                low_cursor.execute(create_cmd)
                insert_cmd = 'insert into break_low (datetime,code,name,low_price,last_price,last_price_date) values (%s,%s,%s,%s,%s,%s);'
                insert_data = (date, code, df.loc[i]['name'], cur_low, mins, mins_date)
                low_cursor.execute(insert_cmd, insert_data)
                low_db.commit()

    def get_lowest(self, code, date, current_date):
        '''
        返回个股某一年最低价
        :param code: 股票代码
        :param date: 年份
        :return:
        '''
        date = date + '-01-01'
        cmd = 'select * from `{}` where datetime > \'{}\' and datetime <\'{}\''.format(code, date, current_date)

        try:
            df = pd.read_sql(cmd, self.engine, index_col='index')
        except Exception as e:
            print(e)
            return None, None
        # print(df.dtypes)
        # 不知道为啥，这里的类型发生改变
        if len(df) < 1:
            return None, None
        df['low'] = df['low'].astype('float64')
        idx = df['low'].idxmin()
        min_date = df.loc[idx]
        return min_date['datetime'], min_date['low']

    def get_highest(self, code, date):
        '''
        返回个股某一年最高价
        :param code: 股票代码
        :param date: 年份
        :return:
        '''
        date = date + '-01-01'
        cmd = 'select high from `{}` where datetime > \'{}\''.format(code, date)
        df = pd.read_sql(cmd, self.engine)
        return df['high'].max()

    def save_to_excel(self, df, filename, encoding='gbk'):
        try:
            df.to_csv('temp.csv', encoding=encoding, index=False)
            df = pd.read_csv('temp.csv', encoding=encoding, dtype={'code': str})
            df.to_excel(filename, encoding=encoding)
            return True
        except Exception as e:
            print("Save to excel faile")
            print(e)
            return None

    # 专门用来存储数据，数据保存为excel，不必每次都要从网络读取
    def store_data(self):
        # 预测
        # year_2016=ts.forecast_data(2016, 4)
        # self.save_to_excel(year_2016,'2016-profit.xls')

        # year_2017=ts.forecast_data(2017, 4)
        # self.save_to_excel(year_2017,'2017-profit.xls')
        # 盈利能力
        # profit_2016=ts.get_profit_data(2016,4)
        # profit_2017=ts.get_profit_data(2017,3)
        # self.save_to_excel(profit_2016, '2016-profit.xls')
        # self.save_to_excel(profit_2017, '2017-3rdprofit.xls')
        # 股票基本信息
        # basic=ts.get_stock_basics()
        # basic.to_csv('temp.xls',encoding='gbk')
        # df=pd.read_csv('temp.xls',encoding='gbk',dtype={'code':str})
        # # print(df)
        # self.save_to_excel(df,'Markets.xls')

        # 基本面 每股净资产<1
        df = ts.get_report_data(2017, 3)
        self.save_to_excel(df, '2017-3rd-report.xls')

    def to_be_ST(self):
        '''
        df_2016=pd.read_excel('2016-profit.xls',dtype={'code':str})
        df_2017=pd.read_excel('2017-3rdprofit.xls',dtype={'code':str})
        loss_2016=set(df_2016[df_2016['net_profits']<0]['code'])
        loss_2017=set(df_2017[df_2017['net_profits']<0]['code'])
        st= list(loss_2016 & loss_2017)
        basic=pd.read_excel('Markets.xls',dtype={'code':str})
        # print(basic.head(5))
        # for x in st:
        #     print(x)
        # print(basic[basic['code']==st])
        for i in st:
            print(basic[basic['code']==i][['code','name']])
        '''

        # 每股净资产小于0
        df_bpvs = pd.read_excel('2017-3rd-report.xls', dtype={'code': str})
        # print(df_bpvs.head())
        print(df_bpvs[df_bpvs['bvps'] < 0][['code', 'name']])

    # 返回新股信息
    def get_new_stock(self, start='2010', end='2011'):
        '''
        :param start: 开始年份 如 '2010'
        :param end:  结束年份 如 '2011'
        :return:
        '''
        df = pd.read_sql('tb_basic_info', self.engine, index_col='index')
        df = df[df['list_date'] != 0]
        df['list_date'] = pd.to_datetime(df['list_date'], format='%Y%m%d')
        df = df.set_index('list_date', drop=True)

        new_stock = df[start:end]  # 返回df格式
        return new_stock

    def plot_new_stock_distibution(self, df, start, end):
        years = OrderedDict()
        values = []
        for year in range(start, end):
            years[year] = len(df[str(year)])
            values.append(len(df[str(year)]))
        x = np.arange(1994, 2019)
        plt.figure(figsize=(10, 9))
        rect = plt.bar(x, values)
        self.rect_show(rect)
        plt.xticks(x[::2])
        plt.show()

    def rect_show(self, rects):
        for rect in rects:
            height = rect.get_height()
            plt.text(rect.get_x(), 1.05 * height, '%s' % int(height))

    # 只是用于测试，展示数据
    def show(self):
        df = self.get_new_stock()
        # print(df)

    # 返回黑名单的代码
    def get_blacklist(self):
        # conn=self.conn('db_stock','local')
        cursor = self.conn.cursor()
        query = 'select CODE from tb_blacklist'
        cursor.execute(query)
        ret = cursor.fetchall()
        return [i[0] for i in ret]


# 可转债过滤
class Filter_CB(object):

    def __init__(self):
        self.engine = DBSelector().get_engine('db_stock', 'tencent-1c')
        # self.bonds = pd.read_sql('tb_bond_jisilu', con=self.engine)

    # 获取新股的可转债，一般比较猛
    def get_new_stock_bond(self, start='2017', end='2019'):
        '''

        :return: 返回新股对应的转债数据 df
        '''
        obj = FilterStock()
        new_stock_df = obj.get_new_stock(start, end)
        # index是timeToMarket

        code_list = list(new_stock_df['code'].values)
        new_stock_bond_df = self.bonds[self.bonds['正股代码'].isin(code_list)]
        for code in new_stock_bond_df['正股代码'].values:
            print(code)
            t_market = new_stock_df[new_stock_df['code'] == code].index.values[0]

        return new_stock_bond_df

    def show(self):
        df = self.get_new_stock_bond()
        print(df)

    def run(self):
        df = pd.read_sql('tb_bond_jisilu', con=self.engine)
        want_cb_df = df[((df['可转债价格'] <= 125) & (df['溢价率'] <= 15))]
        want_cb_df = want_cb_df[['可转债代码', '可转债名称', '可转债价格', '溢价率']]
        # want_cb_df.rename(columns={'可转债代码':''})
        want_cb_df.loc[:, '优先级'] = 0  # 默认都为0

        want_cb_df.loc[:, '当前日期'] = datetime.date.today()

        try:
            want_cb_df.to_sql('tb_stock_candidates', con=self.engine, if_exists='replace')
        except Exception as e:
            print(e)


def main():
    # obj = Filter_Stock()
    # obj.show()
    # obj.get_blacklist()
    # obj.get_ST()
    # obj.get_achievement()
    # obj.get_location('深圳')
    # obj.break_low()
    # obj.break_low('2017-11-17')
    # print(type(obj.get_lowest('300333','2017')))
    # print(obj.get_lowest('300333', '2017'))
    # print(obj.get_highest('300333', '2017'))
    # obj.break_low('2017-11-17')

    # obj.store_data()
    # obj.to_be_ST()
    # obj.get_location()
    # print(obj.get_new_stock())
    # obj.get_location()

    obj_cb = Filter_CB()
    obj_cb.show()


if __name__ == '__main__':
    main()
