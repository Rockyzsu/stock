import fire
import pandas as pd
from data_source import DataSource
import matplotlib.pyplot as plt

class Runner:

    def __init__(self,opt):
        self.app = DataSource()

        self.opt = opt
        self.funcOption = {'fetch': self.fetch, 'bt': self.backtrade,'other':self.other}
        self.func = self.funcOption.get(opt)

    def fetch(self):
        self.app.all_market_data()

    def other(self):
        print(self.app.get_closed_fund_netvalue('160143'))

    def backtrade(self):
        _df = self.app.get_data_from_mongo()
        self.N = 10
        df = _df.set_index(['净值日期','code']).unstack()['日增长率']
        df.index = pd.to_datetime(df.index)

        day_return = df
        signal = df.apply(self.selectTopN, axis=1)
        tmpdf = signal.iloc[range(0, len(signal), 5)]

        pnl = (signal * day_return).sum(axis=1) / self.N
        print('收益率{}'.format(pnl))
        (pnl + 1).cumprod().plot(figsize=(10, 5), grid=True)
        plt.show()
        return pnl

    def week(self):
        tmpdf = signal.iloc[range(0, len(signal), 5)]
        week_selected_df = pd.DataFrame(index=signal.index)
        week_selected_df = week_selected_df.join(tmpdf)
        week_selected_df = week_selected_df.fillna(method='pad')
        pnl = (week_selected_df * day_return).sum(axis=1) / N
        (pnl + 1).cumprod().plot(figsize=(10, 5), grid=True)


    def selectTopN(self,tmp):
        tmp = tmp.copy()
        symbols = tmp.nsmallest(self.N).index
        tmp[:] = 0
        tmp[symbols] = 1
        return tmp


    def run(self):
        self.func()


def main(func):
    app = Runner(func)
    app.run()

if __name__ == '__main__':
    fire.Fire(main)
