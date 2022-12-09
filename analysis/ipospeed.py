# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
# 查看ipo速度 和指数的关系
import tushare as ts
import pandas as pd
import numpy as np
from pandas import Series
import pyecharts.options as opts
from pyecharts.charts import Line

pd.set_option('display.max_rows', None)


class IPOSpeed():

    def __init__(self):

        self.ipo = ts.new_stocks()
        # 日期转化
        self.ipo['ipo_date'] = self.ipo['ipo_date'].astype('datetime64')
        self.start = self.ipo['ipo_date'].iloc[-1]
        self.end = self.ipo['ipo_date'].values[0]
        # 转化类型

    def comparation(self):
        delta = 30
        count_list = []
        profit_list = []
        date_list =[]

        self.period = self.end + np.timedelta64(delta, 'D')
        start_date = self.start

        while start_date < self.end:
            first_date = start_date
            start_date = start_date + np.timedelta64(delta, 'D')
            result = self.ipo[(self.ipo['ipo_date'] >= first_date) & (self.ipo['ipo_date'] < start_date)]
            count = len(result)

            start_date_str = pd.to_datetime(str(first_date)).strftime('%Y-%m-%d')
            end_date_str = pd.to_datetime(str(start_date)).strftime('%Y-%m-%d')

            #index_data = ts.get_k_data('399001', index=True, start=start_date_str, end=end_date_str)
            index_data = ts.get_k_data('000001', index=True, start=start_date_str, end=end_date_str)
            # 大盘（深圳，考虑到国家队在上证的操作） 在30天内的收益
            index_data = index_data
            start_v = index_data['close'].values[0]
            end_v = index_data['close'].values[-1]
            p = round((end_v - start_v) / start_v * 100, 2)
            count_list.append(count)
            profit_list.append(p)
            date_list.append(end_date_str)

        return count_list, profit_list,date_list

    def draw(self):
        count_list, profit_list,date_list = self.comparation()
        title1='IPO数量'
        title2='指数走势'
        title='相关性走势'

        c = (
            Line()
            .add_xaxis(date_list)
            .add_yaxis(title1, count_list, is_smooth=True,
                       label_opts=opts.LabelOpts(is_show=False),
                       linestyle_opts=opts.LineStyleOpts(width=2, color='rgb(255, 0, 0)'),
                       ).add_yaxis(title2, profit_list, is_smooth=True,
                                   linestyle_opts=opts.LineStyleOpts(width=2, color='rgb(0, 0, 255)'),
                                   label_opts=opts.LabelOpts(is_show=False),
                                   ).set_global_opts(
                title_opts=opts.TitleOpts(title=title),
                xaxis_opts=opts.AxisOpts(
                    name='日期',
                    min_interval=1,
                    splitline_opts=opts.SplitLineOpts(is_show=True),
                    axislabel_opts=opts.LabelOpts(rotate=55),
                ),
                yaxis_opts=opts.AxisOpts(name='收益率%',
                                         interval=3,
                                         # min_=_ymin - 2,
                                         # max_=_ymax + 2,
                                         splitline_opts=opts.SplitLineOpts(is_show=True),
                                         )
            )
            .set_colors(['red', 'blue'])  # 点的颜色
            .render(f"../data/IPO与指数走势相关性.html")
        )
        count_s1 = Series(count_list, index=date_list)
        profit_s1 = Series(profit_list, index=date_list)

        relation_ratio = count_s1.corr(profit_s1) # 相关系数
        print('IPO发行数据与沪深300的相关系数 ',relation_ratio)


def main():
    obj = IPOSpeed()
    obj.draw()

if __name__=='__main__':
    main()
