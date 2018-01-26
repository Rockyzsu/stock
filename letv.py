#-*-coding=utf-8-*-
import BaseService
import tushare as ts
import matplotlib.pyplot as plt
def main():
    BaseService.changeDir()
    df = ts.get_today_ticks('300104')
    total_vol=df['volume'].sum()
    big_deal=df[df['volume']>=100]['volume'].sum()
    percent=float(big_deal)/total_vol*100
    print percent
    df['volume'].plot(kind='hist',use_index=False,grid=True)
    plt.show()


if __name__ == '__main__':
    main()