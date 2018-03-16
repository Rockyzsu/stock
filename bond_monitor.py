#-*-coding=utf-8
'''
可转债监控
'''
import tushare as ts
from setting import get_engine
engine = get_engine('db_bond')
import pandas as pd
import datetime
class ConvertBond():

    def __init__(self):
        self.conn=ts.get_apis()
        self.allBonds=ts.new_cbonds(pause=2)
        self.onSellBond=self.allBonds.dropna(subset=['marketprice'])
        self.today=datetime.datetime.now().strftime('%Y-%m-%d')

    def stockPrice(self,code):
        stock_df = ts.get_realtime_quotes(code)
        price = float(stock_df['price'].values[0])
        return price

    def dataframe(self):
        price_list=[]
        for code in self.onSellBond['scode']:
            price_list.append(self.stockPrice(code))
        self.onSellBond['stock_price']=price_list
        self.onSellBond['ratio'] = self.onSellBond['stock_price'] / self.onSellBond['convprice'] * 100 - self.onSellBond['marketprice']
        self.onSellBond['Updated']=self.today
        self.onSellBond.to_sql('tb_bond',engine,if_exists='replace')

    def closed(self):
        ts.close_apis(self.conn)

def calculation():
    df=pd.read_sql('bond',engine,index_col='index')
    df['ration']=df['stock_price']/df['convprice']*100-df['marketprice']
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