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
from configure.settings import DBSelector

DUMP_DB = True

logger = loguru.logger

class ETFBase:

    def __init__(self, history_data):
        self.etf_df = ak.fund_etf_category_sina(symbol="ETF基金")
        self.current_date = datetime.date.today().strftime('%Y-%m-%d')
        self.code_list = self.etf_df['代码'].tolist()
        self.conn = DBSelector().get_engine('db_etf', 'tencent-1c')
        self.db = DBSelector().get_mysql_conn('db_etf','tencent-1c'
                                            )
        self.cursor = self.db.cursor()

        self.etf_df.to_sql('tb_{}'.format(self.current_date),
                               con=self.conn,
                               if_exists='replace',
                               index_label='index',
                               )


class ETFRunner(ETFBase):

    def __init__(self,history_data):
        self.history_data=history_data
        super(ETFRunner, self).__init__(history_data)

    def history_data_all(self):
        # 获取历史所有数据

        for code in self.code_list:
            # print(code)
            try:
                df = ak.fund_etf_hist_sina(symbol=code)
            except Exception as e:
                logger.error('{} error'.format(code))
            else:
                df.to_sql('tb_{}_history'.format(code), con=self.conn)
                time.sleep(1 + random.random())

    def update_current_data(self):

        for index,row in self.etf_df.iterrows():
            code = row['代码']
            # print(code)
            open=float(row['今开'])
            high=float(row['最高'])
            low=float(row['最低'])
            close=float(row['最新价'])
            volume=float(row['成交量'])

            self._update_current_data(code,self.current_date,open,high,low,close,volume)


    def _update_current_data(self,code,date,open,high,low,close,volume):

        sql_str = 'insert into `tb_{}_history` (date,open,high,low,close,volume) values (%s,%s,%s,%s,%s,%s)'.format(code)
        try:
            self.cursor.execute(sql_str,(date,open,high,low,close,volume))
        except Exception as e:
            logger.error(e)
            self.db.rollback()

        else:
            logger.info('正在更新{} '.format(code))
            self.db.commit()

    def fix(self):
        for code in self.code_list:

            sql = 'delete from tb_{}_history where `index` is null and `date`=%s'.format(code)
            try:
                self.cursor.execute(sql,args=('2023-02-08',))
            except Exception as e:
                logger.error(e)
            else:

                self.db.commit()
                logger.info('删除{}'.format(code))

    def run(self):
        if self.history_data:
            self.history_data_all()
        else:
            self.update_current_data()


def main(history_data=False):
    app = ETFRunner(history_data)
    app.run()
    # app.fix()

if __name__ == '__main__':
    fire.Fire(main)
