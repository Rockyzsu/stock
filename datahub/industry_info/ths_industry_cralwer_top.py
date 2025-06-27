import time
from parsel import Selector
import requests
from data_dump import DataDump
from cookies_generator import gen_cookies
import re

URL = 'https://data.10jqka.com.cn/funds/hyzjl/field/tradezdf/order/desc/page/{}/ajax/1/free/1/'

payload = {}
headers = {
    'Accept': 'text/html, */*; q=0.01',
    'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Referer': 'https://data.10jqka.com.cn/funds/hyzjl/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

dataObj = DataDump()
dataObj.create_table()


def update_cookies():
    c = gen_cookies()
    cookie = 'v={}'.format(c)
    headers['Cookie'] = cookie
    headers['Hexin-V'] = c
    return headers


WAIT_TIME = 10


def crawl(url, is_detail=False):
    _headers = update_cookies()
    try:
        print('crawl {} '.format(url))
        response = requests.request("GET", url, headers=_headers, data=payload)
    except Exception as e:
        print(e)
        time.sleep(WAIT_TIME)
        return None
    else:
        time.sleep(WAIT_TIME)
        return response.text


top_count = 10


def parser(html):
    resp = Selector(text=html)
    top_raise_list = resp.xpath('//table[@class="m-table m-pager-table"]/tbody/tr')
    industry_data = []
    if len(top_raise_list) == 0:
        print('异常，数据为空')
        print(html)

    for tr in top_raise_list[:top_count]:
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

        industry_id = dataObj.insert_industry(industry['name'], industry['pct_change'], industry['industry_detail_url'],
                                              industry_code)
        print('插入 ', industry_id)
        print(name, pct_change, industry_detail_url)
        detail_response = crawl(industry_detail_url, is_detail=True)

        detail_info = parse_detail(detail_response, industry_code)
        # print(detail_info)
        industry['details'] = detail_info
        industry_data.append(industry)
    return industry_data


detail_url = 'https://q.10jqka.com.cn/thshy/detail/code/{}/page/{}'


def parse_detail(html, industry_code):
    # 分页
    # print(html)
    if 'forbid' in html:
        print('详情页被封了')
        # print(html)
        return []

    # total_page = get_total_page(html)
    total_page = 1  # 强制变1
    if total_page == 1:
        return _parse_detail(html, industry_code)
    else:
        detail_list = [_parse_detail(html, industry_code)]
        for i in range(2, total_page + 1):
            html = crawl(detail_url.format(industry_code, i))
            data = _parse_detail(html, industry_code)
            detail_list.append(data)

        return detail_list


def _parse_detail(html, industry_code):
    resp = Selector(text=html)
    industry_detail = resp.xpath('//table[@class="m-table m-pager-table"]/tbody/tr')
    industry_stock_data = []
    if (len(industry_detail) == 0):
        print('数据为空，详情页')
        print(html)
        return []

    for tr in industry_detail:
        stock_obj = {}
        stock_code = tr.xpath('./td[2]/a/text()').get()
        stock_name = tr.xpath('./td[3]/a/text()').get()
        percent = tr.xpath('./td[5]/text()').get()
        turnover_rate = tr.xpath('./td[8]/text()').get()
        vol = tr.xpath('./td[11]/text()').get() # 1.2 亿
        print('vol',vol)
        vol = vol.replace('亿','')
        vol = float(vol) * 100000000
        # stock_pct_change = tr.xpath('./td[@class="tr cur c-rise"]/text()').get()
        # print(stock_pct_change)
        # print(stock_name, stock_pct_change)
        stock_obj['stock_code'] = stock_code
        stock_obj['stock_name'] = stock_name
        # stock_obj['stock_pct_change'] = stock_pct_change
        stock_obj['percent'] = percent
        stock_obj['vol'] = vol
        stock_obj['turnover_rate'] = turnover_rate

        dataObj.insert_stock(industry_code, stock_obj['stock_code'], stock_obj['stock_name'], stock_obj['percent'],
                             stock_obj['vol'],
                             stock_obj['turnover_rate'])

        industry_stock_data.append(stock_obj)

    return industry_stock_data


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


def dumpData(data):
    for industry in data:
        industry_id = dataObj.insert_industry(industry['name'], industry['pct_change'], industry['industry_detail_url'])
        for stock in industry['details']:
            dataObj.insert_stock(industry_id, stock['stock_code'], stock['stock_name'], stock['percent'], stock['vol'],
                                 stock['turnover_rate'])


def main():
    next_url = 'https://q.10jqka.com.cn/thshy/'
    html = crawl(next_url)
    parser(html)


if __name__ == "__main__":
    main()
