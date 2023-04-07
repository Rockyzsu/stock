from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import backtrader as bt
import os
import sys
import datetime



# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('日志 ： %s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        #这个名字可以随意该
        print('datas',self.datas)
        self.dataclose_change = self.datas[0].close
        print('init',self.datas[0])
        self.order = None

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def log(self,txt,dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('-1', self.datas[0].datetime.date(-1)) # 上一天
        # print('1', self.datas[-2].datetime.date(0))
        print(' 0',dt)
        print('dataclose_change ',self.dataclose_change[0])

    def next(self):
        # Simply log the closing price of the series from the reference
        # self.log('收盘价, %.2f' % self.dataclose_change[0])
        # if self.dataclose_change[0]>self.dataclose_change[-1]:
        #     self.log('当天收盘价, %.2f ， 昨天收盘价 %.2f' % (self.dataclose_change[0],self.dataclose_change[-1]))
        #     self.log('买入价%.2f' % self.dataclose_change[0])
        #     self.buy()

        if self.order:
            return

            # Check if we are in the market
        if not self.position:

            # Not yet ... we MIGHT BUY if ...
            if self.dataclose_change[0] < self.dataclose_change[-1]:
                # current close less than previous close

                if self.dataclose_change[-1] < self.dataclose_change[-2]:
                    # previous close less than the previous close

                    # BUY, BUY, BUY!!! (with default parameters)
                    self.log('BUY CREATE, %.2f' % self.dataclose_change[0])

                    # Keep track of the created order to avoid a 2nd order
                    self.order = self.buy()

        else:

            # Already in the market ... we might sell
            if len(self) >= (self.bar_executed + 5):
                # SELL, SELL, SELL!!! (with all possible default parameters)
                self.log('SELL CREATE, %.2f' % self.dataclose_change[0])

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()

def main():
    cerebro = bt.Cerebro()
    cerebro.addstrategy(TestStrategy)
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '/home/xda/othergit/backtrader/datas/nvda-1999-2014.txt')

    print(modpath)
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(2014, 1, 2),
        # Do not pass values after this date
        todate=datetime.datetime(2014, 9, 1),
        reverse=False)

    # Add the Data Feed to Cerebro
    cerebro.adddata(data)
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)

    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    cerebro.run()

    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

if __name__ == '__main__':
    main()