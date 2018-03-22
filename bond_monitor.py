#-*-coding=utf-8
'''
可转债监控
'''
# from __future__ import division
import tushare as ts
from setting import get_engine
import pandas as pd
import datetime,time
from numpy import inf
engine = get_engine('db_bond')


class ConvertBond():

    def __init__(self):
        self.conn=ts.get_apis()
        self.available_bonds = pd.read_sql('tb_bond_jisilu', engine, index_col='index')[u'可转债代码'].values
        self.allBonds=ts.new_cbonds(default=0,pause=2)
        self.onSellBond=self.allBonds.dropna(subset=['marketprice'])
        self.today=datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        self.total = self.onSellBond[self.onSellBond['bcode'].isin(self.available_bonds)]


    def stockPrice(self,code):
        stock_df = ts.quotes(code,conn=self.conn)
        price = float(stock_df['price'].values[0])
        print code,price
        return price

    def dataframe(self):
        s_price_list=[]
        b_price_list=[]
        for code in self.total['scode'].values:
            s_price_list.append(self.stockPrice(code))
            # b_price_list.append(self.stockPrice(str(code[1])))
            # time.sleep(2)

        self.total['stock_price']=s_price_list
        self.total=self.total[self.total['stock_price']!=0]
        # self.total['bond_price']=b_price_list
        self.total['Bond Value'] = self.total['stock_price'] / self.total['convprice']*100
        self.total['ratio']=(self.total['marketprice']/self.total['Bond Value']-1)*100
        self.total['ratio']=self.total['ratio'].map(lambda x:round(x,2))
        self.total['Bond Value']=self.total['Bond Value'].map(lambda x:round(x,2))
        self.total['Updated']=self.today
        print self.total

        self.total.to_sql('tb_bond',engine,if_exists='replace')

    def closed(self):
        ts.close_apis(self.conn)

def calculation():
    df=pd.read_sql('bond',engine,index_col='index')
    df['ration']=(df['stock_price']/df['convprice']*100-df['marketprice'])/(df['stock_price']/df['convprice']*100)
    # print df[df['ration']>0]
    df.to_sql('tb_bond',engine,if_exists='replace')

def main():
    bond=ConvertBond()
    bond.dataframe()
    bond.closed()
    # calculation()

if __name__=='__main__':
    main()
    print 'done'