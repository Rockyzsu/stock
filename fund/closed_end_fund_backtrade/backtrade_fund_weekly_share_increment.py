# 作者公众号：可转债量化分析
import pandas as pd
from fund_data_source import DataSource
import numpy as np
from loguru import logger

class Runner:

    def __init__(self, opt):
        self.app = DataSource()
        self.opt = opt
        self.funcOption = {'fetch': self.fetch, 'bt': self.backtrade, 'other': self.other}
        self.func = self.funcOption.get(opt)
        self.debug = False
        self.MSG = '总资产{:.2f},总收益率{:.2f}%'

    def fetch(self):
        self.app.all_market_data()

    def other(self):
        self.compare_all_market()

    def position_intialize(self):
        '''
        回测参数 设置
        '''
        logger.info("start backtrade, initialling")

        self.Position = {}  # 存储的是 code和份额
        self.cash = 100 * 10000  # 100W
        self.origin_cash = self.cash
        self.N = 10  # 最大持有个数
        self.interval = 10  # 调仓周期

        self.start = '2018-01-01'  # 修改起始时间
        self.source = 'mongo'  # '本地数据库'
        # self.source = 'akshare'  # 'akshare' # 数据源

        self.profit_list = []

    def get_max_withdraw(self,indexs):
        max_withdraw = 0
        max_date_index = 0
        last_high = indexs[0]

        for index, current in enumerate(indexs):
            # 遍历所有数据
            if current > last_high:
                last_high = current
                continue

            if (last_high - current) / last_high > max_withdraw:
                # 找到一个最大值时，保存其位置
                max_withdraw = (last_high - current) / last_high
                max_date_index = index

        return max_withdraw  # 变成百分比

    def daily_netvalue(self,df_copy,i,profit,date):
        '''
        非调仓阶段 获取持仓的收益率
        '''
        holding_list = list(self.Position.keys())
        if i + self.interval - 1 >= len(df_copy):
            return

        for code in holding_list:
            fund_netvalue = df_copy.iloc[i + self.interval - 1][code]
            profit += self.Position[code] * fund_netvalue

        ratio = profit / self.origin_cash * 100 - 100
        self.profit_list.append({'date': date, 'profit': ratio})

    def backtrade(self):
        self.position_intialize()

        _df = self.app.get_data(self.source)

        _df['净值日期'] = _df['净值日期'].astype('datetime64[ns]')
        df_copy = _df.set_index(['净值日期', 'code']).unstack()['累计净值']
        df = _df.set_index(['净值日期', 'code']).unstack()['日增长率']
        df.index = pd.to_datetime(df.index, format='%Y-%m-%d')
        df_copy.index = pd.to_datetime(df_copy.index, format='%Y-%m-%d')

        df = df.loc[self.start:]
        df_copy = df_copy.loc[self.start:]

        final_profit = None

        for i in range(len(df)):
            profit = self.cash
            date = df.iloc[i].name.date()
            if i%self.interval!=0:
                self.daily_netvalue(df_copy,i,profit,date)
                continue

            t = df.iloc[i:i + self.interval].sum()
            top_netvalue_increase = t.nlargest(self.N)
            target = top_netvalue_increase.index

            if i + self.interval - 1 >= len(df):
                continue

            target_result = df_copy.iloc[i + self.interval - 1].loc[target]

            if all(target_result.isnull()):
                logger.error('empty value occur!')
                continue

            holding_list = list(self.Position.keys())

            for code in holding_list:
                fund_netvalue = df_copy.iloc[i + self.interval - 1][code]

                profit += self.Position[code] * fund_netvalue
                # [Rocky]: 卖出
                if code not in target:
                    # 计算卖出的·金额
                    self.cash += self.Position[code] * fund_netvalue  # 放入现金
                    # 移除仓位
                    del self.Position[code]
                    msg = '{} 卖出{}'.format(date, code)
                    logger.info(msg)
            ratio = profit / self.origin_cash * 100 - 100
            logger.info(self.MSG.format(profit, ratio))
            self.profit_list.append({'date': date, 'profit': ratio})

            for code in target:
                if code not in self.Position and len(self.Position) <= self.N:

                    if np.isnan(df_copy.iloc[i + self.interval - 1][code]):
                        continue
                    fund_netvalue = df_copy.iloc[i + self.interval - 1][code]
                    self.Position[code] = self.cash / (self.N - len(self.Position)) / fund_netvalue
                    self.cash -= self.Position[code] * fund_netvalue
                    msg = '{} 买入{}，基金当前净值 {},买入份额{:.2f}'.format(date, code, fund_netvalue, self.Position[code])
                    logger.info(msg)

        self.evaluate()

    def evaluate(self):
        _profit_list = [i.get('profit')/100+1 for i in self.profit_list]
        max_withdraw = self.get_max_withdraw(_profit_list)
        last_value = self.profit_list[-1].get('profit')
        logger.info('总收益率{:.2f}%'.format(last_value))
        logger.info('策略最大回撤为{:.2f}%'.format(max_withdraw*100))
        profit_df = pd.DataFrame(self.profit_list)
        profit_df = profit_df.dropna(axis=0)
        profit_df.to_excel('backtrade.xlsx',encoding='utf8')
        ax = profit_df.plot(x='date', y='profit', grid=True, title='closed fund profit', rot=45, figsize=(12, 8))
        fig = ax.get_figure()
        fig.savefig('封基轮动收益率曲线.png')

    def each_fund_profit(self,row):
        row = row.dropna()
        # print(row)
        percent = (row[-1] - row[0]) / row[0]
        year = (row.index[-1]-row.index[0]).days/365
        yiled_ratio = (1+percent)**(1/year)-1
        return yiled_ratio*100

    def compare_all_market(self):
        '''
        所有封基的中位数
        '''
        self.position_intialize()
        _df = self.app.get_data(self.source)

        _df['净值日期'] = _df['净值日期'].astype('datetime64[ns]')
        df_copy = _df.set_index(['净值日期', 'code']).unstack()['累计净值']
        df_copy.index = pd.to_datetime(df_copy.index, format='%Y-%m-%d')
        df_copy = df_copy.loc[self.start:]

        result = df_copy.apply(self.each_fund_profit,axis=0)
        print(result)
        print('年化收益率中位数',np.median(result))
        print('年化收益率平均',np.mean(result))

    def run(self):
        self.func()