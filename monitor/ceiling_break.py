# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''

# 股票封板监控

import time
import datetime
import tushare as ts
import pandas as pd
import threading
from common.BaseService import BaseService
from configure.settings import DBSelector

EXCEPTION_TIME_OUT = 60
NORMAL_TIME_OUT = 3
TIME_RESET = 60 * 5


# 监测涨停板开板监测
class BreakMonitor(BaseService):

    def __init__(self, send=True):
        super(BreakMonitor, self).__init__()
        self.send = send
        self.DB = DBSelector()
        self.engine = self.DB.get_engine('db_stock', 'qq')
        self.bases = pd.read_sql('tb_basic_info', self.engine, index_col='index')

    def read_stock_list(self, file=None):
        if file:
            with open(file, 'r') as f:
                monitor_list = f.readlines()
                monitor_list = list(map(lambda x: x.strip(), monitor_list))
        else:
            monitor_list = ['300100']

        return monitor_list

    def percent(self, current, close):
        return (current - close) * 1.0 / close * 100

    # 开板提示
    def break_ceil(self, code):
        print(threading.current_thread().name)

        while 1:

            # 交易时间
            if self.trading_time() != 0:
                break

            try:
                df = ts.get_realtime_quotes(code)
            except Exception as e:
                self.logger.error(e)
                time.sleep(5)
                continue

            v = float(df['b1_v'].values[0])

            if self.percent(float(df.iloc[0]['price']), float(df.iloc[0]['pre_close'])) < 9:
                if self.send == True:
                    title = f'{code}已经板了'
                    self.notify(title)
                    break

            if v <= 1000:
                print(datetime.datetime.now().strftime("%H:%M:%S"))
                print(u"小于万手，小心！跑")
                print(self.bases[self.bases['code'] == code]['name'].values[0])
                if self.send == True:
                    title = f'{code}开板了'
                    self.notify(title)

            time.sleep(10)

    def monitor_break(self):
        thread_num = len(self.read_stock_list())  # 线程数和股票输一样
        thread_list = []
        for i in range(thread_num):
            t = threading.Thread(target=self.break_ceil, args=(self.read_stock_list()[i],))
            thread_list.append(t)

        for j in thread_list:
            j.start()

        for k in thread_list:
            k.join()


if __name__ == '__main__':
    obj = BreakMonitor(send=True)
    obj.monitor_break()
