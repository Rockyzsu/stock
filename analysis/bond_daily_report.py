import sys

sys.path.append('..')
import pandas as pd
from configure.settings import DBSelector
from configure.util import calendar

engine = DBSelector().get_engine('db_jisilu')

date_list = calendar('2024-01-01', '2024-12-31')

for date in date_list:
    table = 'tb_jsl_{}'.format(date)
    df = pd.read_sql(table, engine)
    trade_amount = df['成交额(万元)'].sum()
    print(date, round(trade_amount/10000,2),'亿')
