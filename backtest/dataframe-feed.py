from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse

import backtrader as bt
import backtrader.feeds as btfeeds
from datapath import ROOT
import pandas
import datetime

def convert_time(x):
    return datetime.datetime.fromtimestamp(int(x/1000))

def runstrat():
    args = parse_args()

    # Create a cerebro entity
    cerebro = bt.Cerebro(stdstats=False)

    # Add a strategy
    cerebro.addstrategy(bt.Strategy)

    # Get a pandas dataframe

    # datapath = (ROOT + '2006-day-001.txt')
    ROOT = '/home/xda/github/stock_strategy/backtrader-code/'
    datapath = (ROOT + 'BNBUSDT.csv')

    # Simulate the header row isn't there if noheaders requested
    skiprows = 1 if args.noheaders else 0
    header = None if args.noheaders else 0

    dataframe = pandas.read_csv(datapath,
                                skiprows=skiprows,
                                header=header,
                                )

    dataframe['open_time']=dataframe['open_time'].map(convert_time)
    dataframe=dataframe.set_index('open_time',drop=True)

    if not args.noprint:
        print('--------------------------------------------------')
        print(dataframe)
        print('--------------------------------------------------')

    # Pass it to the backtrader datafeed and add it to the cerebro
    data = bt.feeds.PandasData(dataname=dataframe)

    cerebro.adddata(data)

    # Run over everything
    cerebro.run()

    # Plot the result
    cerebro.plot(style='bar')


def parse_args():
    parser = argparse.ArgumentParser(
        description='Pandas test script')

    parser.add_argument('--noheaders', action='store_true', default=False,
                        required=False,
                        help='Do not use header rows')

    parser.add_argument('--noprint', action='store_true', default=False,
                        help='Print the dataframe')

    return parser.parse_args()


if __name__ == '__main__':
    runstrat()