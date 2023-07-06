# -* coding=utf8 *-
# 基金某个时间段的涨幅
import datetime
import sys
import loguru
import fire
import pandas as pd

sys.path.append('..')
from sqlhelper import SQLHelper

logger = loguru.logger

BUILT_DAY = 60  # 成立时间
MORE_THAN_DAY = 60
IGNORE_LIST = ['sz159001']


class ETFFinder(SQLHelper):

    def __init__(self, date=None):
        super(ETFFinder, self).__init__(host='tencent-1c', db_name='db_etf')

        if date is None:
            self.current_date = datetime.date.today().strftime('%Y-%m-%d')
        else:
            self.current_date = date

        self.etf_df = pd.read_sql('tb_{}'.format(self.current_date), con=self.conn)
        self.code_list = self.etf_df['代码'].tolist()
        for code in IGNORE_LIST:
            if code in self.code_list:
                self.code_list.remove(code)

    def range_increment(self):

        for code in self.code_list:
            if code.startswith('sz'):
                long_laid_down = self.long_bottom_down(code)
                if long_laid_down:
                    logger.info('{}满足需求'.format(code))

    def query_data(self, code, count):

        # 去当前时间往前推 BUILT_DAY 的数据
        # volume 单位为股 ，
        sql_str = 'select `close`,`date`,`volume` from `tb_{}_history` order by `date` desc limit {}'.format(
            code, count)
        return self.query(sql_str, args=None)

    def count(self, code):
        sql_str = 'select count(*) from `tb_{}_history`'.format(code)
        ret = self.query(sql_str, args=None)
        return ret[0][0]

    def high_low_count(self):
        day = 250  # 一年
        # for code in self.code_list:
        #     is_low,is_high = self.is_low_high(code,day)
        low_count = 0
        high_count = 0

        for code in self.code_list:
            low, high = self._low_high_process(code, day)
            if low:
                low_count += 1
            if high:
                high_count += 1

        logger.info('创新低数量{}'.format(low_count))
        logger.info('创新高数量{}'.format(high_count))

    def _low_high_process(self, code, day):

        low, high = self.is_low_high(code, day)
        current_price = self.latest(code)

        lowest = False
        highest = False

        if current_price <= low and self.count(code) > MORE_THAN_DAY:
            logger.info('{} 创新低'.format(code))
            lowest = True
        if current_price >= high and self.count(code) > MORE_THAN_DAY:
            highest = True
            logger.info('{} 创新高'.format(code))

        return lowest, highest

    def update_result(self,data):
        sql='insert into `` () values ()'

    def latest(self, code):
        sql_str = '''
                    SELECT `close`
                    FROM `tb_{}_history`
                    ORDER BY `date` DESC
                    LIMIT 1'''.format(code)
        ret = self.query(sql_str, args=None)
        return ret[0][0]

    def is_low_high(self, code, day):
        '''
        创新低和创新高
        '''

        sql_str = '''SELECT MIN(high),MAX(high) FROM (
                    SELECT `high`
                    FROM `tb_{}_history`
                    ORDER BY `date` DESC
                    LIMIT {}
                    ) AS subquery;'''.format(code, day)
        ret = self.query(sql_str, args=None)
        _low = ret[0][0]
        _high = ret[0][1]
        return _low, _high

    def ma_line_up_factor(self, code, ret_data):
        # 均线上穿 因子
        close_list = []
        if len(ret_data) < BUILT_DAY:
            # 成立时间不够
            logger.info('{} data lenght not meet {}, {}'.format(code, BUILT_DAY, len(ret_data)))
            return False
        for close, date, volume in ret_data:
            close_list.append(close)

        close_series = pd.Series(close_list)
        ma5 = close_series.rolling(5).mean().iloc[-1]
        ma10 = close_series.rolling(10).mean().iloc[-1]
        if (ma5 > ma10) and (close_list[-1] > ma5):
            return True
        else:
            return False

    def long_bottom_factor(self, code, ret_data):
        data = [i[0] for i in ret_data]
        s = pd.Series(data)
        volume = [i[2] for i in ret_data]
        v = pd.Series(volume[-5:])
        avg_v = v.mean()
        avg = s.mean()
        current_price = data[-1]
        if abs((current_price - avg) / avg) < (5 / 100) and (avg_v / 100 > 1000000):
            return True
        else:
            return False

    def long_bottom_down(self, code):
        # 横盘很久的ETF
        LONG_DAY = 100
        ret_data = self.query_data(code, LONG_DAY)
        meet_ma_up = self.long_bottom_factor(code, ret_data)
        if meet_ma_up:
            logger.info('{}满足需求'.format(code))

    def get_increment(self):
        for code in self.code_list:
            long_laid_down = self.long_bottom_down(code)
            if long_laid_down:
                logger.info('{}满足需求'.format(code))


# TODO 有可能是新的ETF

def main(opt=None, date=None):
    app = ETFFinder(date)
    print(type(opt))
    func_dict = {0: app.range_increment,
                 1: app.high_low_count}
    func_dict.get(opt)()


if __name__ == '__main__':
    fire.Fire(main)
