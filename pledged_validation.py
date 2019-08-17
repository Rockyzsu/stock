#-*-coding=utf-8-*-
import json
import tushare as ts
import pandas as pd
from setting import get_engine
import matplotlib.pyplot as plt

# 股权质押数据整理

with open('codes.txt','r') as f:
	# s= f.read()
	codes=json.load(f)

stocks=codes.get('example1')
engine=get_engine('db_stock')

# for key in codes.get('example1').keys():
	# print(key, codes.get('example1').get(key))
# df1=pd.DataFrame()
def pledge_info():
	df=ts.stock_pledged()
	df.to_sql('tb_pledged_base',engine,if_exists='replace')

	df_list=[]

	for stock in stocks:
		df_list.append(df[df['code']==stock])

	df=pd.concat(df_list)
	# print(df)
	df=df.reset_index(drop=True)
	# print(df)
	df= df.sort_values('p_ratio',ascending=False)
	df['code']=df['code'].astype('str')
	df['rest_ratio']=df['rest_pledged']/df['totals']*100
	df['rest_ratio']=map(lambda x:round(x,2),df['rest_ratio'])
	df['unrest_ratio']=df['unrest_pledged']/df['totals']*100
	df['unrest_ratio']=map(lambda x:round(x,2),df['unrest_ratio'])

	# print(df.info())
	# print(df)
	# print(df.sort_values('deals',ascending=False))
	# df.to_csv('pledge_my_stock.csv')

def pledged_detail():
	df=ts.pledged_detail()
	print(df.tail(10))
	# for stock in stocks:
	# 	if len(df[df['code']==stock])!=0:
	# 		print(df[df['code']==stock])
	# df.to_csv('pledge_all_stock.csv')
	df.to_sql('tb_pledged_detail',engine)

def do_calculation():
	df=pd.read_sql('tb_pledged_base',engine,index_col='index')
	# print(df)
	# df['unrest_ratio']=df['unrest_pledged']/df['totals']*100
	# df['rest_ratio']=df['rest_pledged']/df['totals']*100
	# df['unrest_ratio']=map(lambda x:round(x,2),df['unrest_ratio'])
	# df['rest_ratio']=map(lambda x:round(x,2),df['rest_ratio'])
	# df.to_sql('tb_pledged_base',engine,if_exists='replace')
	print('median ',df['p_ratio'].median())
	print('mean ',df['p_ratio'].mean())
	print('std ',df['p_ratio'].std())
	print('var ',df['p_ratio'].var())
	plt.figure()
	plt.hist(df['p_ratio'],20)
	# plt.hist(df['p_ratio'],10,normed=True)
	plt.show()

# pledge_info()
# pledged_detail()
do_calculation()