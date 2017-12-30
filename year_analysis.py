#-*-coding=utf-8-*-
import os
import pandas as pd
import matplotlib.pyplot as plt
def stock_analysis():
    df=pd.read_excel('2017-year.xls',encoding='gbk')
    print 'mean:\n',df['price_change'].mean()
    print 'max:\n',df['price_change'].max()
    print 'min:\n',df['price_change'].min()
    print 'middle\n',df['price_change'].median()
    plt.figure()
    df['price_change'].plot.hist()
    plt.show()


def main():
    stock_analysis()

if __name__ == '__main__':
    data_path=os.path.join(os.getcwd(),'data')
    os.chdir(data_path)
    main()