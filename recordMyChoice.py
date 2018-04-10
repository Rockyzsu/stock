# -*-coding=utf-8-*-
# 记录每天选股后的收益，用于跟踪每一只自选股
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
import datetime, os, xlrd, time
from xlutils.copy import copy
import tushare as ts
from setting import get_mysql_conn
import codecs


class Prediction_rate():

    def __init__(self):
        self.today_stock = ts.get_today_all()
        now = datetime.datetime.now()
        self.today = now.strftime("%Y-%m-%d")
        # weekday=now+datetime.timedelta(days=-2)
        # weekday=weekday.strftime("%Y-%m-%d")
        # print weekday
        # today=now.strftime('%Y-%m-%d')
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
        print "%d*%d" % (nrow, ncol)
        row_start = nrow
        wb_copy = copy(wb)
        sheet = wb_copy.get_sheet(0)
        # 调用 write 函数写入 info write(1,1,'Hello')

        content = []
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
持股信息保存到Mysql数据库
'''


def holding_stock_sql():
    path = os.path.join(os.path.dirname(__file__), 'data', 'mystock.csv')
    if not os.path.exists(path):
        return

    conn = get_mysql_conn('db_stock')
    cur = conn.cursor()
    create_table_cmd = u'CREATE TABLE IF NOT EXISTS `tb_profit` (`证券代码` CHAR (6),`证券名称` VARCHAR (16), `保本价` FLOAT,`股票余额` INT,`盈亏比例` FLOAT,`盈亏` FLOAT, `市值` FLOAT);'
    try:
        cur.execute(create_table_cmd)
        conn.commit()
    except Exception, e:
        print e
        conn.rollback()
    with codecs.open(path,'r',encoding='utf-8') as f:
        content = f.readlines()

    for i in range(1,len(content)):
        code,name,safe_price,count= content[i].strip().split(',')[:4]
        print code,name,safe_price,count
        insert_cmd=u'INSERT INTO `tb_profit`  (`证券代码`,`证券名称`,`保本价`,`股票余额`) VALUES(\"%s\",\"%s\",\"%s\",\"%s\");' %(code.zfill(6),name,safe_price,count)
        try:
            cur.execute(insert_cmd)
            conn.commit()
        except Exception,e:
            print e
            conn.rollback()
    conn.close()


if __name__ == "__main__":
    # obj=Prediction_rate()
    # obj.first_recode()
    holding_stock_sql()
