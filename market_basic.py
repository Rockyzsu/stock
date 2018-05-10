# -*-coding=utf-8-*-

__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
股市基本面
'''

from setting import  get_engine

import tushare as ts

engine = get_engine('db_finance_report')
def year_report(year):
    df0 = ts.get_report_data(year, 4)
    df0.to_sql(str(year)+'_main',engine)
    df1 = ts.get_profit_data(year, 4)
    df1.to_sql(str(year)+'_profit',engine)
    df2 = ts.get_growth_data(year, 4)
    df2.to_sql(str(year)+'_growth',engine)
    df3 = ts.get_debtpaying_data(year, 4)
    df3.to_sql(str(year)+'_debtpaying',engine)
    df4 = ts.get_cashflow_data(year, 4)
    df4.to_sql(str(year)+'_cashflow',engine)



def main():
    for i in range(2010,2018):
        year_report(i)

if __name__=='__main__':
    main()