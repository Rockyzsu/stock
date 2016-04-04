import tushare as ts
import sys
import numpy as np
import pandas as pd

class StockBox:
	
	def base_function(self,id):
		if id == None:
			print "Input stock id please "
			return
		stockInfo = ts.get_hist_data(id)
		#print type(stockInfo)
		#print stockInfo.head()
		#print stockInfo.dtypes
		df = ts.get_stock_basics()
		data=df.ix[id]['timeToMarket']
		print data		
		ts.get_today_all()		
		

def main():
	stockBox =StockBox()
	stockBox.base_function("300333")
	#pandas_test=Pandas_test()
	#pandas_test.test_function()	

class Pandas_test:
	def test_function(self):
		dates=pd.date_range("20160501",periods=10)
		print dates

if __name__=="__main__":
	main()
	
