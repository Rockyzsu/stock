# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
# 搜索大单进入的个股
import sys
sys.path.append('..')
from common.BaseService import BaseService
import tushare as ts
import pandas as pd

pd.set_option('display.max_rows', None)


class Monitor_Stock(BaseService):
    def __init__(self):
        super(Monitor_Stock, self).__init__('../log/bigdeal.log')

    # 大于某手的大单
    def getBigDeal(self, code, vol):
        df = ts.get_today_ticks(code) #获取tick数据
        print('df ', df)
        t = df[df['vol'] > vol]
        # s = df[df['amount'] > 100000000]
        # r = df[df['volume'] > vol * 10]


        if  len(t)>0:
            self.logger.info("Big volume {}".format(code))
            # self.logger.info(self.base[self.base['code'] == str(code)]['name'].values[0])
            # self.logger.info(t)

    def init_market(self):
        '''
        获取全市场
        '''
        from configure.settings import get_tushare_pro
        pro = get_tushare_pro()
        data = pro.stock_basic(exchange='SSE', list_status='L')
        # print(data)
        data=data[~data['ts_code'].str.startswith("A")]
        return data['symbol'].tolist()


    def run(self):
        code_list = self.init_market()
        for i in code_list:
            try:
                # print(i)
                self.getBigDeal(i, 1000)
            except Exception as e:
                print(e)


def main():
    app = Monitor_Stock()
    # app.getBigDeal('002451',2000)
    app.run()
    # app.init_market()

if __name__ == '__main__':
    main()
