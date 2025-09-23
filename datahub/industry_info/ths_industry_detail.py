import requests
import time
from parsel import Selector
import requests
from data_dump import DataDump
from cookies_generator import gen_cookies
import re

# hexin='Aycl1pkNDM-2QIhDE8yt9QRStlD0rP5MVYl_FvmXQc_f6EmOAXyL3mVQD1oK'
BASIC_URL = "https://q.10jqka.com.cn/thshy/detail/field/199112/order/desc/page/{}/ajax/1/code/{}"

payload = {}


def get_total_page(html):
    page_info = Selector(text=html).xpath('//span[@class="page_info"]/text()').get()
    if page_info is None:
        # print(html)
        print('page number info not found,only 1 page')
        return 1

    pages = page_info.split('/')
    if len(pages) == 2:
        return int(pages[1])
    else:
        raise ValueError('page info error')


def read_cookies():

    api_url = "http://127.0.0.1:7000/ths/hexin"
    payload = {}
    headers = {}
    response = requests.request("GET", api_url, headers=headers, data=payload)
    data=response.json()
    hexin = data['hexin']
    return hexin


def get_headers():
    # hexin = gen_cookies()
    # print(hexin)
    hexin = read_cookies()
    headers  = {
  'Accept': 'text/html, */*; q=0.01',
  'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6',
  'Cache-Control': 'no-cache',
  'Connection': 'keep-alive',
  'Cookie': 'Hm_lvt_722143063e4892925903024537075d0d=1739618766; Hm_lpvt_722143063e4892925903024537075d0d=1739618766; HMACCOUNT=8144A39C4F4A22E9; Hm_lvt_929f8b362150b1f77b477230541dbbc2=1739618767; Hm_lpvt_929f8b362150b1f77b477230541dbbc2=1739618767; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1739618767; historystock=000627; spversion=20130314; Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1742117683; u_ukey=A10702B8689642C6BE607730E11E6E4A; u_uver=1.0.0; u_dpass=xm%2F5h1ycNmxybkXT5OHYvn%2BzS8FOyrdJXsUWRxtn%2BBUMTzTPYe8995kQarA0qO%2FsHi80LrSsTFH9a%2B6rtRvqGg%3D%3D; u_did=33B5B946911B443683389E0F857364C0; u_ttype=WEB; ttype=WEB; user=MDpyb2NreXpzdTo6Tm9uZTo1MDA6MjM5NDg0ODc0OjcsMTExMTExMTExMTEsNDA7NDQsMTEsNDA7NiwxLDQwOzUsMSw0MDsxLDEwMSw0MDsyLDEsNDA7MywxLDQwOzUsMSw0MDs4LDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAxLDQwOzEwMiwxLDQwOjI3Ojo6MjI5NDg0ODc0OjE3NDM5NTI1MDc6OjoxNDI4NDEyNjIwOjYwNDgwMDowOjFmODFlMDA0YWZmYmU5ODIyNTNmZmM4MmVmZDRjYWZjYTpkZWZhdWx0XzQ6MA%3D%3D; userid=229484874; u_name=rockyzsu; escapename=rockyzsu; ticket=a5ac51d899a5e0f16b5ec60c0caac153; user_status=0; utk=9d55d410895cb948f07e9d387c45eb83; v={}'.format(hexin),
  'Pragma': 'no-cache',
  'Referer': 'https://q.10jqka.com.cn/thshy/detail/code/881117/',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
  'X-Requested-With': 'XMLHttpRequest',
  'hexin-v': hexin,
  'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"'
}
    return headers


def crawl(url):
    while 1:

        _headers = get_headers()
        try:
            response = requests.request("GET", url, headers=_headers, data=payload)

            html = response.text
            resp = Selector(text=html)
            industry_detail = resp.xpath('//table[@class="m-table m-pager-table"]/tbody/tr')
            if (len(industry_detail) == 0):
                print('数据为空，详情页')
                print('需要更新cookies')
                input('请更新cookies,然后按回车继续')
                _headers = get_headers()
            else:
                return html

        except Exception as e:
            print(e)
            raise ValueError('请求异常，退出')


dataObj = DataDump()
dataObj.create_table_fixed_name()


def get_crawl_list():
    result_tuple = dataObj.query_queue()
    industry_code_list = []
    for item in result_tuple:
        industry_code = item[4]
        industry_name = item[1]
        industry_code_list.append((industry_code, industry_name))
    return industry_code_list


def _parse_detail(html, industry_code):
    resp = Selector(text=html)
    industry_detail = resp.xpath('//table[@class="m-table m-pager-table"]/tbody/tr')
    industry_stock_data = []
    if (len(industry_detail) == 0):
        print('数据为空，详情页')
        raise ValueError('数据为空，详情页,退出')
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

        dataObj.insert_stock_fix_table(industry_code, stock_obj['stock_code'], stock_obj['stock_name'],
                                       stock_obj['percent'],
                                       stock_obj['vol'],
                                       stock_obj['turnover_rate'])

        industry_stock_data.append(stock_obj)

    return True


def process_detail(industry_code):
    # industry_code = 881102
    url = BASIC_URL.format(1, industry_code)
    html = crawl(url)
    page = get_total_page(html)
    print(page)
    dataObj.update_page_num(industry_code, page)

    result = _parse_detail(html, industry_code)
    if page > 1:
        result_list = []
        for p in range(2, page + 1):
            time.sleep(1)
            print('processing page {}'.format(p))
            url = BASIC_URL.format(p, industry_code)
            html = crawl(url)
            result_list.append(_parse_detail(html, industry_code))
            time.sleep(1)

        if all((result_list)):
            dataObj.update_done(industry_code)
    else:
        if result:
            dataObj.update_done(industry_code)


def main():
    industry_code_list = get_crawl_list()
    for item in industry_code_list:
        code = item[0]
        name = item[1]
        print('procesing industry code {} name {}'.format(code, name))
        process_detail(code)
        time.sleep(1)


if __name__ == '__main__':
    main()
