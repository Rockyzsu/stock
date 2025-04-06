import requests
import time
from parsel import Selector
import requests
from data_dump import DataDump
from cookies_generator import gen_cookies
import re


BASIC_URL = "https://q.10jqka.com.cn/thshy/detail/field/199112/order/desc/page/{}/ajax/1/code/{}"

payload = {}
headers = {
  'Accept': 'text/html, */*; q=0.01',
  'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6',
  'Cache-Control': 'no-cache',
  'Connection': 'keep-alive',
  'Cookie': 'Hm_lvt_722143063e4892925903024537075d0d=1739618766; Hm_lpvt_722143063e4892925903024537075d0d=1739618766; HMACCOUNT=8144A39C4F4A22E9; Hm_lvt_929f8b362150b1f77b477230541dbbc2=1739618767; Hm_lpvt_929f8b362150b1f77b477230541dbbc2=1739618767; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1739618767; historystock=000627; spversion=20130314; Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1742117683; v=A4eFNjltrO9NKChjoEQN1eSyFjBUjFkTtWTf61l1oeQ_66muYVzrvsUwbzZq',
  'Pragma': 'no-cache',
  'Referer': 'https://q.10jqka.com.cn/thshy/detail/code/881102/',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
  'X-Requested-With': 'XMLHttpRequest',
  'hexin-v': 'A4eFNjltrO9NKChjoEQN1eSyFjBUjFkTtWTf61l1oeQ_66muYVzrvsUwbzZq',
  'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"'
}

def get_total_page(html):
    page_info = Selector(text=html).xpath('//span[@class="page_info"]/text()').get()
    if page_info is None:
        # print(html)
        print('page info not found')
        return 1

    pages = page_info.split('/')
    if len(pages) == 2:
        return int(pages[1])
    else:
        raise ValueError('page info error')


def crawl(url):
    try:
        response = requests.request("GET", url, headers=headers, data=payload)

        return response.text
    except Exception as e:
        print(e)
        return None

dataObj = DataDump()
dataObj.create_table_fixed_name()

def get_crawl_list():
    result_tuple = dataObj.query_queue()
    industry_code_list = []
    for item in result_tuple:
        industry_code = item[4]
        industry_code_list.append(industry_code)
    return industry_code_list

def _parse_detail(html, industry_code):
    resp = Selector(text=html)
    industry_detail = resp.xpath('//table[@class="m-table m-pager-table"]/tbody/tr')
    industry_stock_data = []
    if (len(industry_detail) == 0):
        print('数据为空，详情页')
        return False

    for tr in industry_detail:
        stock_obj = {}
        stock_code = tr.xpath('./td[2]/a/text()').get()
        stock_name = tr.xpath('./td[3]/a/text()').get()
        percent = tr.xpath('./td[5]/text()').get()
        turnover_rate = tr.xpath('./td[8]/text()').get()
        vol = tr.xpath('./td[11]/text()').get()
        # stock_pct_change = tr.xpath('./td[@class="tr cur c-rise"]/text()').get()
        # print(stock_pct_change)
        # print(stock_name, stock_pct_change)
        stock_obj['stock_code'] = stock_code
        stock_obj['stock_name'] = stock_name
        # stock_obj['stock_pct_change'] = stock_pct_change
        stock_obj['percent'] = percent
        stock_obj['vol'] = vol
        stock_obj['turnover_rate'] = turnover_rate

        dataObj.insert_stock_fix_table(industry_code, stock_obj['stock_code'], stock_obj['stock_name'], stock_obj['percent'],
                             stock_obj['vol'],
                             stock_obj['turnover_rate'])

        industry_stock_data.append(stock_obj)

    return True

def process_detail(industry_code):
    # industry_code = 881102
    url = BASIC_URL.format(1,industry_code)
    html = crawl(url)
    page = get_total_page(html)
    print(page)
    dataObj.update_page_num(industry_code, page)

    result = _parse_detail(html, industry_code)
    if page>1:
        result_list = []
        for p in range(2,page+1):
            url = BASIC_URL.format(p,industry_code)
            html = crawl(url)
            result_list.append( _parse_detail(html, industry_code))
            time.sleep(5)

        if all((result_list)):
            dataObj.update_done(industry_code)
    else:
        if result:
            dataObj.update_done(industry_code)




def main():
    industry_code_list = get_crawl_list()
    for code in industry_code_list:
        process_detail(code)
        time.sleep(5)

if __name__ == '__main__':
    main()

