#-*-coding=utf-8-*-
import os
import pandas as pd
import matplotlib.pyplot as plt
from setting import DATA_PATH

# 分析年度的数据
def stock_analysis():
    df=pd.read_excel('2017-year.xls',encoding='gbk')
    print('mean:\n',df['price_change'].mean())
    print('max:\n',df['price_change'].max())
    print('min:\n',df['price_change'].min())
    print('middle\n',df['price_change'].median())
    plt.figure()
    df['price_change'].plot.hist()
    plt.show()


def main():
    stock_analysis()

if __name__ == '__main__':
    data_path =r'C:\OneDrive\Stock_Data'
    # data_path=DATA_PATH
    os.chdir(data_path)
    main()