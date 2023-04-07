import backtrader as bt
import pandas as pd
import datetime as dt


class MyStrategy(bt.Strategy):
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.sma_period = self.params.sma_period
        self.sma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.sma_period)

    def next(self):
        if not self.position:
            if self.dataclose[0] > self.sma[0] and self.dataclose[-1] <= self.sma[-1]:
                self.buy()
        else:
            if self.dataclose[0] < self.sma[0] and self.dataclose[-1] >= self.sma[-1]:
                self.sell()


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    from datapath import ROOT
    datapath = ROOT+ 'orcl-1995-2014.txt'  # 可以公众号：可转债量化分析 后台留言 backtrade数据 获取

    dataframe = pd.read_csv(datapath)
    dataframe['Date'] = pd.to_datetime(dataframe['Date'])
    dataframe.set_index('Date', inplace=True)

    data = bt.feeds.PandasData(dataname=dataframe)
    cerebro.adddata(data)
    strategy = MyStrategy()

    cerebro.addstrategy(strategy )  # 设置10日均线周期

    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.002)

    cerebro.run()
    cerebro.plot(style='candle')