# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
email: weigesysu@qq.com
'''
import datetime
import tushare as ts
import os
from setting import get_engine, get_mysql_conn
import pandas as pd

# pandas.set_option('display.max_rows',None)
daily_engine = get_engine('daily')
history_engine = get_engine('history')


class Filter_Stock():
    def __init__(self):
        current = os.getcwd()
        work_space = os.path.join(current, 'data')
        if os.path.exists(work_space) == False:
            os.mkdir(work_space)
        os.chdir(work_space)
        print os.getcwd()
        self.today = datetime.datetime.now().strftime("%Y-%m-%d")

    def get_location(self, loc):
        df = ts.get_area_classified()
        print df

    def get_ST(self):
        # 暂停上市
        zt = ts.get_suspended()
        print zt
        # 终止上市
        zz = ts.get_terminated()
        print zz

    def get_achievement(self):
        fc = ts.forecast_data(2016, 4)
        print fc

    def daily_market(self):
        '''
        保存每天收盘后的市场行情
        :return:
        '''
        df = ts.get_today_all()
        print df
        try:
            df.to_sql(self.today, daily_engine, if_exists='replace')
        except Exception, e:
            print e
        print "Save {} data to MySQL".format(self.today)

    def break_low(self, date):
        '''
        筛选出一年内创新低的股票
        :param date: 某一天的日期 ‘'2017-11-11
        :return:
        '''
        cmd = 'select * from `{}`'.format(date)
        df = pd.read_sql(cmd, daily_engine)
        # **** 这里的index需要删除一个
        df_low = pd.DataFrame()

        for i in range(len(df)):
            code = df.loc[i]['code']
            cur_low = df.loc[i]['low']
            mins = self.get_lowest(code, '2017')
            if mins and float(cur_low)<=float(mins):
                print code,
                print df.loc[i]['name']
                print 'year mins ',mins,
                print 'curent mins ',cur_low

    def get_lowest(self, code, date):
        '''
        返回个股某一年最低价
        :param code: 股票代码
        :param date: 年份
        :return:
        '''
        date = date + '-01-01'
        cmd = 'select low from `{}` where datetime > \'{}\''.format(code, date)
        try:
            df = pd.read_sql(cmd, history_engine)
        except Exception,e:
            print e
            return None
        return df['low'].min()

    def get_highest(self, code, date):
        '''
        返回个股某一年最高价
        :param code: 股票代码
        :param date: 年份
        :return:
        '''
        date = date + '-01-01'
        cmd = 'select high from `{}` where datetime > \'{}\''.format(code, date)
        df = pd.read_sql(cmd, history_engine)
        return df['high'].max()


def main():
    obj = Filter_Stock()
    # obj.get_ST()
    # obj.get_achievement()
    # obj.get_location(u'深圳')
    # obj.break_low()
    # obj.break_low('2017-11-17')
    # print type(obj.get_lowest('300333','2017'))
    #print obj.get_lowest('300333', '2017')
    #print obj.get_highest('300333', '2017')
    obj.break_low('2017-11-17')

if __name__ == '__main__':
    main()
