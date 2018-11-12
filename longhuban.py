#-*-coding=utf-8-*-

import requests
import re
import json
def get_content(url,retry=5):
	headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'}
	while retry >0:
		try:
			r = requests.get(url,headers=headers)
			if r.status_code == 200 and len(r.text) >0:
				return r.text
		except Exception as e:
			print(e)
			retry-=1

		if retry == 0 :
			return None

def convert_json(url):
	content =  get_content(url)
	if content is None:
		return
	lhb_date = []
	try:
		# print(content)
		js = re.findall("var dateList=(.*?);",content,re.S)[0]
		# print(type(js))
		js_data = json.loads(js)
		print(js_data)
		lhb_date = js_data.get('data')
	except Exception as e:
		print(e)
		return

def convert_json(url,pattern):
	content =  get_content(url)
	if content is None:
		return
	lhb_date = []
	try:
		# print(content)
		js = re.findall(pattern,content,re.S)[0]
		# print(type(js))
		js_data = json.loads(js)
		# print(js_data)
		lhb_date = js_data.get('data')
		# print(lhb_date)
		return lhb_date
		# for i in lhb_date:
			# print(i)

	except Exception as e:
		print(e)
		return

def get_result():
	code='300333'
	date='20180424'
	# lhb_list_url = 'http://stock.jrj.com.cn/action/lhb/getStockLhbDateList.jspa?vname=dateList&stockcode={}'.format(code)
	requestdetailURL="http://stock.jrj.com.cn/action/lhb/getStockLhbDetatil.jspa?vname=detailInfo&stockcode={}&date={}".format(code,date)
	return convert_json(requestdetailURL,'var detailInfo=(.*?);')