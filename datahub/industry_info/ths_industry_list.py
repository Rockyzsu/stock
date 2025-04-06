import requests
import time
from parsel import Selector
import requests
from data_dump import DataDump
from cookies_generator import gen_cookies
import re

payload = {}
headers = {
  'Accept': 'text/html, */*; q=0.01',
  'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6',
  'Cache-Control': 'no-cache',
  'Connection': 'keep-alive',
  'Cookie': 'Hm_lvt_722143063e4892925903024537075d0d=1739618766; Hm_lpvt_722143063e4892925903024537075d0d=1739618766; HMACCOUNT=8144A39C4F4A22E9; Hm_lvt_929f8b362150b1f77b477230541dbbc2=1739618767; Hm_lpvt_929f8b362150b1f77b477230541dbbc2=1739618767; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1739618767; historystock=000627; spversion=20130314; Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1742117683; v=A1lbqNtHWjlHCgatCW3bo6Z4aE4x5k6KN99xI3sP1xL8CHcwwzZdaMcqgfgI',
  'Pragma': 'no-cache',
  'Referer': 'https://q.10jqka.com.cn/thshy/',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
  'X-Requested-With': 'XMLHttpRequest',
  'hexin-v': 'A1lbqNtHWjlHCgatCW3bo6Z4aE4x5k6KN99xI3sP1xL8CHcwwzZdaMcqgfgI',
  'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"'
}

dataObj = DataDump()
dataObj.create_table_fixed_name()


def crawl(url):
  try:
    response = requests.request("GET", url, headers=headers, data=payload)
    # print(response.text)
    return response.text
  except Exception as e:
    return None

def parser(html):
  resp = Selector(text=html)
  top_raise_list = resp.xpath('//table[@class="m-table m-pager-table"]/tbody/tr')
  industry_data = []
  if len(top_raise_list) == 0:
    print('异常，数据为空')
    # print(html)

  for tr in top_raise_list:
    industry = {}
    name = tr.xpath('./td[2]/a/text()').get()
    industry_detail_url = tr.xpath('./td[2]/a/@href').get()
    pct_change = tr.xpath('./td[3]/text()').get()
    pct_change = float(pct_change.replace('%', ''))
    industry['name'] = name
    industry['pct_change'] = pct_change
    industry['industry_detail_url'] = industry_detail_url
    match = re.search('http://q.10jqka.com.cn/thshy/detail/code/(\d+)', industry_detail_url)
    industry_code = match.group(1)
    industry['industry_code'] = industry_code

    industry_id = dataObj.insert_industry_fix_table(industry['name'], industry['pct_change'], industry['industry_detail_url'],
                                          industry_code)
    print('插入 ', industry_id)
    print(name, pct_change, industry_detail_url)



def main():
  industrty_list_url = "https://q.10jqka.com.cn/thshy/index/field/199112/order/desc/page/{}/ajax/1/"
  for page in range(1, 3):
    url = industrty_list_url.format(page)
    print('crawl {} '.format(url))
    response = crawl(url)
    if response:
      parser(response)
    else:
      print('请求失败')



if __name__ == '__main__':
    main()
