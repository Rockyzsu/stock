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
        #cmd = 'select * from `{}`'.format(date)
        df = pd.read_sql_table(date, daily_engine,index_col='index')
        # **** 这里的index需要删除一个
        low_db= get_mysql_conn('db_selection')
        low_cursor = low_db.cursor()
        for i in range(len(df)):
            code = df.loc[i]['code']
            cur_low = df.loc[i]['low']

            mins_date,mins = self.get_lowest(code, '2017',date)
            if not mins_date:
                continue
            if mins and float(cur_low)<=float(mins) and float(cur_low) !=0.0:
                print code,
                print df.loc[i]['name']
                print 'year mins {} at {}'.format(mins,mins_date)
                print 'curent mins ',cur_low
                create_cmd = 'create table if not exists break_low' \
                             '(`index` int primary key auto_increment,datetime datetime,code text,name text,low_price float,last_price float, last_price_date datetime);'
                low_cursor.execute(create_cmd)
                insert_cmd = 'insert into break_low (datetime,code,name,low_price,last_price,last_price_date) values (%s,%s,%s,%s,%s,%s);'
                insert_data = (date,code,df.loc[i]['name'],cur_low,mins,mins_date)
                low_cursor.execute(insert_cmd,insert_data)
                low_db.commit()


    def get_lowest(self, code, date,current_date):
        '''
        返回个股某一年最低价
        :param code: 股票代码
        :param date: 年份
        :return:
        '''
        date = date + '-01-01'
        cmd = 'select * from `{}` where datetime > \'{}\' and datetime <\'{}\''.format(code, date,current_date)

        try:
            df = pd.read_sql(cmd, history_engine,index_col='index')
        except Exception,e:
            print e
            return None,None
        #print df.dtypes
        # 不知道为啥，这里的类型发生改变
        if len(df)<1:
            return None,None
        df['low']=df['low'].astype('float64')
        idx= df['low'].idxmin()
        min_date= df.loc[idx]
        return min_date['datetime'],min_date['low']



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
