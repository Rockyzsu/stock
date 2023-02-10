# -* coding=utf8 *-
# 基金某个时间段的涨幅
import datetime
import random
import time
import akshare as ak
import sys
import loguru
import fire

sys.path.append('..')

DUMP_DB = False  # 不写入数据库

logger = loguru.logger

from sqlhelper import SQLHelper


class ETFBase(SQLHelper):

    def __init__(self):
        super(ETFBase, self).__init__(host='tencent-1c', db_name='db_etf')
        self.etf_df = ak.fund_etf_category_sina(symbol="ETF基金")
        self.current_date = datetime.date.today().strftime('%Y-%m-%d')
        self.code_list = self.etf_df['代码'].tolist()

        if DUMP_DB:
            self.etf_df.to_sql('tb_{}'.format(self.current_date),
                               con=self.conn,
                               if_exists='replace',
                               index_label='index',
                               )


class ETFDataCrawler(ETFBase):

    def __init__(self, history_data):
        self.history_data = history_data
        super(ETFDataCrawler, self).__init__()

    def history_data_all(self):
        # 获取历史所有数据

        for code in self.code_list:
            try:
                df = ak.fund_etf_hist_sina(symbol=code)
            except Exception as e:
                logger.error('{} error {}'.format(code,e))
            else:
                df.to_sql('tb_{}_history'.format(code), con=self.conn)
                time.sleep(1 + random.random())

    def update_current_data(self):

        for index, row in self.etf_df.iterrows():
            code = row['代码']
            open = float(row['今开'])
            high = float(row['最高'])
            low = float(row['最低'])
            close = float(row['最新价'])
            volume = float(row['成交量'])

            self._update_current_data(code, self.current_date, open, high, low, close, volume)

    def _update_current_data(self, code, date, open, high, low, close, volume):

        sql_str = 'insert into `tb_{}_history` (date,open,high,low,close,volume) values (%s,%s,%s,%s,%s,%s)'.format(code)
        args = (date, open, high, low, close, volume)
        if not self.update(sql_str, args):
            logger.error('{} 更新失败'.format(code))

    def update_index(self):
        for code in self.code_list:
            # sql_str = 'drop index idx on `tb_{}_history`'.format(code)
            sql_str = 'create UNIQUE INDEX idx on `tb_{}_history`(`date`)'.format(code)
            if self.update(sql_str):
                logger.info('创建索引{}'.format(code))

    def fix(self):
        for code in self.code_list:
            # sql_str = 'delete from tb_{}_history where `index` is null and `date`=%s'.format(code)
            # args = ('2023-02-10',)
            sql_str = 'alter table `tb_{}_history` drop column `index`'.format(code) # 删除某一列
            args = None
            if not self.update(sql_str, args):
                logger.info('删除{} 失败'.format(code))


    def run(self):
        if self.history_data:
            self.history_data_all()
        else:
            self.update_current_data()


# TODO 有可能是新的ETF

def main(history_data=False):
    app = ETFDataCrawler(history_data)
    app.run()  # 获取数据
    # app.fix()


if __name__ == '__main__':
    fire.Fire(main)
