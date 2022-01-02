# @Time : 2020/2/26 9:38
# @File : fund_raise_speed.py
# 查看基金最后暴力拉伸的
import datetime
import random
import time
from configure.settings import DBSelector
import tushare as ts
import sys
sys.path.append('..')

from common.BaseService import BaseService

class MonitorFund(BaseService):

    def __init__(self):
        super(MonitorFund, self).__init__('../log/monitor_fund.log')
        self.conn = DBSelector().get_mysql_conn('db_stock','qq')

    def fast_speed_up(self):
        table = '2020-02-25'  # 用于获取code列

        today = datetime.datetime.now().strftime('%Y-%m-%d')
        print(today)
        logger = self.logger.info(f'{today}_fund_raise_monitor.log')
        query = 'select `基金代码`,`基金简称` from `2020-02-25`'
        # print(query)
        cursor = self.conn.cursor()
        cursor.execute(query)

        ret = cursor.fetchall()

        code_list = []

        for item in ret:
            code = item[0]
            df = ts.get_realtime_quotes(code)

            close_p = float(df['pre_close'].values[0])
            b1 = float(df['b1_p'].values[0])
            a1 = float(df['a1_p'].values[0])
            percent = (a1 - b1) / close_p * 100
            if percent > 5:
                print(f'{item[0]} {item[1]} 有超过5%的委买卖的差距')
                logger.info(f'{item[0]} {item[1]} 有超过5%的委买卖的差距')

            time.sleep(random.random())

