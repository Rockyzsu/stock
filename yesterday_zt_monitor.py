# -*-coding=utf-8-*-

'''
昨日涨停的今日的实时情况
'''
import datetime
import matplotlib
matplotlib.use("Pdf")
from configure.settings import DBSelector
import pandas as pd
import tushare as ts
from plot_line import plot_stock_line
from common.BaseService import BaseService
from configure.util import notify


# 绘制k线图，今日涨停的k线图
class PlotYesterdayZT(BaseService):

    def __init__(self):
        super(PlotYesterdayZT, self).__init__('log/yester_zdt.log')

    def get_data(self,table,current):
        DB = DBSelector()
        engine = DB.get_engine('db_zdt', 'qq')

        try:
            df = pd.read_sql(table, engine)
        except Exception as e:
            self.logger.error('table_name >>> {}{}'.format(current, table))
            self.logger.error(e)
            return None
        else:
            return df

    def plot_yesterday_zt(self,api,type_name='zrzt', current=datetime.datetime.now().strftime('%Y%m%d')):

        start_data = datetime.datetime.now() + datetime.timedelta(days=-200)
        start_data=start_data.strftime('%Y-%m-%d')
        table_name = type_name
        table = f'{current}{table_name}'

        df = self.get_data(table,current)

        for i in range(len(df)):
            code = df.iloc[i]['代码']
            name = df.iloc[i]['名称']
            plot_stock_line(api,code, name, table_name=table_name, current=current, start=start_data, save=True)


def main():
    # current='20191016'
    current = datetime.datetime.now().strftime('%Y%m%d')
    app = PlotYesterdayZT()
    api =ts.get_apis()
    for plot_type in ['zrzt', 'zdt']:

        try:
            app.plot_yesterday_zt(api,plot_type, current=current)
        except Exception as e:
            notify(title='zdt_plot 出错',desp=f'{__name__}')
            continue

    ts.close_apis(conn=api)

if __name__ == '__main__':
    main()


