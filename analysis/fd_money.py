# @Time : 2020/1/14 0:05
# @File : fd_money.py
# 涨停封单数据

from configure.settings import DBSelector
import datetime
import pyecharts.options as opts
from pyecharts.charts import Line

DAY = 100 # 查看最近的天数


class FDPlot:

    def __init__(self):
        self.dataset=[]
        self.date=[]


    def fetch_data(self):
        DB = DBSelector()
        conn = DB.get_mysql_conn('db_zdt', 'tencent-1c')
        cursor = conn.cursor()

        for d in range(DAY):
            day = datetime.datetime.now() + datetime.timedelta(days=-1 * d)
            sql = 'select sum(`封单金额`) as total_money from `{}zdt`'.format(day.strftime('%Y%m%d'))


            try:
                cursor.execute(sql)
                ret = cursor.fetchone()
                self.dataset.append(int(ret[0]/100000000))
                self.date.append(day.strftime('%Y%m%d'))
            except Exception as e:
                print(e)

    def plot(self):
        self.fetch_data()
        dataset_ = self.dataset[::-1]
        date_ = self.date[::-1]
        title='封单金额（亿）'
        c = (
        Line()
        .add_xaxis(date_)
        .add_yaxis(title, dataset_, is_smooth=True,
        label_opts=opts.LabelOpts(is_show=False),
    linestyle_opts=opts.LineStyleOpts(width=2,color='rgb(255, 0, 0)'),
        ).set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            xaxis_opts=opts.AxisOpts(
                                    name='日期',
                                    splitline_opts=opts.SplitLineOpts(is_show=True),
               axislabel_opts=opts.LabelOpts(rotate=55),
                                    ),
            yaxis_opts=opts.AxisOpts(name=title,
                splitline_opts=opts.SplitLineOpts(is_show=True),
            )
                                        )
                                        .set_colors(['red']) # 点的颜色
        .render("data/最近{}天股票涨停封单.html".format(DAY))
    )



if __name__ == '__main__':
    app = FDPlot()
    app.plot()