# -*-coding=utf-8-*-
# 记录每天选股后的收益，用于跟踪每一只自选股
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
import datetime
import os
import xlrd
import time
from xlutils.copy import copy
import tushare as ts
from configure.settings import get_mysql_conn
import codecs
from configure.settings import LLogger

logger=LLogger('recordMyChoice.log')
class Prediction_rate():

    def __init__(self):
        self.today_stock = ts.get_today_all()
        now = datetime.datetime.now()
        self.today = now.strftime("%Y-%m-%d")
        # weekday=now+datetime.timedelta(days=-2)
        # weekday=weekday.strftime("%Y-%m-%d")
        # print(weekday)
        # TODAY=now.strftime('%Y-%m-%d')
        self.path = os.path.join(os.getcwd(), 'data')
        self.filename = os.path.join(self.path, 'recordMyChoice.xls')

    def stock_pool(self, stock_list):
        pass

    def first_record(self, stockID):
        # stockID_list=['000673']

        wb = xlrd.open_workbook(self.filename)
        table = wb.sheets()[0]
        nrow = table.nrows
        ncol = table.ncols
        print("%d*%d" % (nrow, ncol))
        row_start = nrow
        wb_copy = copy(wb)
        sheet = wb_copy.get_sheet(0)
        # 调用 write 函数写入 info write(1,1,'Hello')

        # content = []
        mystock = self.today_stock[self.today_stock['code'] == stockID]
        name = mystock['name'].values[0]
        in_price = mystock['trade'].values[0]
        current_price = in_price
        profit = 0.0
        content = [self.today, stockID, name, in_price, current_price, profit]

        for i in range(len(content)):
            sheet.write(row_start, i, content[i])

        row_start = row_start + 1

        wb_copy.save(self.filename)

    def update(self):
        # 对已有的进行更新
        pass


'''
持股信息保存到Mysql数据库, 更新，删除
'''


class StockRecord:

    def __init__(self):
        self.conn = get_mysql_conn('db_stock',local=True)
        self.cur = self.conn.cursor()
        self.table_name = 'tb_profit'
        self.today = datetime.datetime.now().strftime('%Y-%m-%d')
        # self.TODAY = '2018-04-13'

    def holding_stock_sql(self):
        path = os.path.join(os.path.dirname(__file__), 'data', 'mystock.csv')
        if not os.path.exists(path):
            return

        create_table_cmd = 'CREATE TABLE IF NOT EXISTS `tb_profit` (`证券代码` CHAR (6),`证券名称` VARCHAR (16), `保本价` FLOAT,`股票余额` INT,`盈亏比例` FLOAT,`盈亏` FLOAT, `市值` FLOAT);'
        try:
            self.cur.execute(create_table_cmd)
            self.conn.commit()
        except Exception as e:
            # print(e)
            logger.log(e)
            self.conn.rollback()
        with codecs.open(path, 'r', encoding='utf-8') as f:
            content = f.readlines()

        for i in range(1, len(content)):
            code, name, safe_price, count = content[i].strip().split(',')[:4]
            print(code, name, safe_price, count)
            insert_cmd = 'INSERT INTO `tb_profit`  (`证券代码`,`证券名称`,`保本价`,`股票余额`) VALUES(\"%s\",\"%s\",\"%s\",\"%s\");' % (
            code.zfill(6), name, safe_price, count)
            self._exe(insert_cmd)

    def delete(self, content):
        name = u"证券名称"
        cmd = u"DELETE FROM `{}` WHERE `{}` = \"{}\"".format(self.table_name, name, content)
        self._exe(cmd)

    def insert(self, code, name, safe_price, count):
        '''

        :param code: 代码
        :param name: 名称
        :param safe_price: 保本价
        :param count: 股票数目
        :return: None
        '''
        insert_cmd = 'INSERT INTO `tb_profit`  (`证券代码`,`证券名称`,`保本价`,`股票余额`) VALUES(\"%s\",\"%s\",\"%s\",\"%s\");' % (
        code.zfill(6), name, safe_price, count)
        self._exe(insert_cmd)

    # 执行mysql语句
    def _exe(self, cmd):
        try:
            self.cur.execute(cmd)
            self.conn.commit()
        except Exception as e:
            # print(e)
            logger.log(e)
            self.conn.rollback()

        return self.cur

    # 更新每天的盈亏情况
    def update_daily(self):

        add_cols = 'ALTER TABLE `{}` ADD `{}` FLOAT;'.format(self.table_name, self.today)
        self._exe(add_cols)
        # self.conn.commit()
        api = ts.get_apis()
        cmd = 'SELECT * FROM `{}`'.format(self.table_name)
        cur = self._exe(cmd)
        for i in cur.fetchall():
            (code, name, safe_price, count, profit_ratio, profit, values, current_price,earn) = i[:9]
            df = ts.quotes(code, conn=api)
            current_price = round(float(df['price'].values[0]), 2)
            values = current_price * count
            last_close = df['last_close'].values[0]
            earn = (current_price - last_close) * count
            profit = (current_price - safe_price) * count
            profit_ratio = round(float(current_price - safe_price) / safe_price * 100, 2)

            update_cmd = 'UPDATE {} SET `盈亏比例`={} ,`盈亏`={}, `市值` ={}, `现价` = {},`{}`={} where `证券代码`= {};'.format(
                self.table_name, profit_ratio, profit, values, current_price, self.today, earn,code)
            # print(update_cmd)
            self._exe(update_cmd)
        ts.close_apis(api)

    # 删除某行
    def update_item(self, code, content):
        cmd = 'UPDATE `{}` SET `保本价`={} where `证券代码`={};'.format(self.table_name, content, code)
        self._exe(cmd)

    def update_sold(self):
        cur = self.conn.cursor()
        tb_name = 'tb_sold_stock'
        cur.execute('select * from {}'.format(tb_name))
        content = cur.fetchall()
        db_daily = get_mysql_conn('db_daily')
        db_cursor=db_daily.cursor()
        stock_table = datetime.datetime.now().strftime('%Y-%m-%d')
        # stock_table = '2018-05-02'
        for i in content:
            cmd='select `trade` from `{}` where `code`=\'{}\''.format(stock_table,i[0])
            print(cmd)
            db_cursor.execute(cmd)
            ret = db_cursor.fetchone()
            sold_price = i[3]
            percentange =round(float(ret[0]- sold_price)/sold_price*100,2)
            update_cmd = 'update  `{}` set `当前价`={} ,`卖出后涨跌幅`= {} where `代码`=\'{}\''.format(tb_name,ret[0],percentange,i[0])
            print(update_cmd)
            cur.execute(update_cmd)
            self.conn.commit()

if __name__ == "__main__":

    if ts.is_holiday(datetime.datetime.now().strftime('%Y-%m-%d')):
        exit(0)
    # obj=Prediction_rate()
    # obj.first_recode()
    # holding_stock_sql()
    obj = StockRecord()
    # obj.delete('深F120')
    # obj.insert('300580','贝斯特',19.88,200)
    obj.update_daily()
    obj.update_sold()
    # obj.update_item('300580',32.568)
