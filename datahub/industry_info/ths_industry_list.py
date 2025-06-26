import sys

sys.path.append('../../')
from configure.settings import config
from parsel import Selector
import requests
from configure.util import send_message_via_wechat
from data_dump import DataDump
import re
from loguru import logger

# 每日更新
logger.add('ths_industry_list.log', rotation='10 MB', level='INFO', encoding='utf-8')

API_HOST = config['API_HOST']
payload = {}

dataObj = DataDump()
dataObj.create_table(only_industry=True)


def get_headers():
    hexin = read_cookies()
    headers = {
        'Accept': 'text/html, */*; q=0.01',
        'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'Hm_lvt_722143063e4892925903024537075d0d=1739618766; Hm_lpvt_722143063e4892925903024537075d0d=1739618766; HMACCOUNT=8144A39C4F4A22E9; Hm_lvt_929f8b362150b1f77b477230541dbbc2=1739618767; Hm_lpvt_929f8b362150b1f77b477230541dbbc2=1739618767; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1739618767; historystock=000627; spversion=20130314; Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1742117683; u_ukey=A10702B8689642C6BE607730E11E6E4A; u_uver=1.0.0; u_dpass=xm%2F5h1ycNmxybkXT5OHYvn%2BzS8FOyrdJXsUWRxtn%2BBUMTzTPYe8995kQarA0qO%2FsHi80LrSsTFH9a%2B6rtRvqGg%3D%3D; u_did=33B5B946911B443683389E0F857364C0; u_ttype=WEB; ttype=WEB; user=MDpyb2NreXpzdTo6Tm9uZTo1MDA6MjM5NDg0ODc0OjcsMTExMTExMTExMTEsNDA7NDQsMTEsNDA7NiwxLDQwOzUsMSw0MDsxLDEwMSw0MDsyLDEsNDA7MywxLDQwOzUsMSw0MDs4LDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAxLDQwOzEwMiwxLDQwOjI3Ojo6MjI5NDg0ODc0OjE3NDM5NTI1MDc6OjoxNDI4NDEyNjIwOjYwNDgwMDowOjFmODFlMDA0YWZmYmU5ODIyNTNmZmM4MmVmZDRjYWZjYTpkZWZhdWx0XzQ6MA%3D%3D; userid=229484874; u_name=rockyzsu; escapename=rockyzsu; ticket=a5ac51d899a5e0f16b5ec60c0caac153; user_status=0; utk=9d55d410895cb948f07e9d387c45eb83; v={}'.format(
            hexin),
        'Pragma': 'no-cache',
        'Referer': 'https://q.10jqka.com.cn/thshy/detail/code/881117/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'hexin-v': hexin,

    }
    return headers


def read_cookies():
    api_url = "{}/api/ths/hexin".format(API_HOST)
    payload = {}
    headers = {}
    response = requests.request("GET", api_url, headers=headers, data=payload)
    data = response.json()
    hexin = data['hexin']
    return hexin


def crawl(url):
    try:
        _headers = get_headers()

        response = requests.request("GET", url, headers=_headers, data=payload)

        # print(response.text)
        return response.text
    except Exception as e:
        return None


def parser(html):
    resp = Selector(text=html)
    top_raise_list = resp.xpath('//table[@class="m-table m-pager-table"]/tbody/tr')
    if len(top_raise_list) == 0:
        logger.info('异常，数据为空')

    for tr in top_raise_list:
        industry = {}
        name = tr.xpath('./td[2]/a/text()').get()
        industry_detail_url = tr.xpath('./td[2]/a/@href').get()
        pct_change = tr.xpath('./td[3]/text()').get()
        pct_change = float(pct_change.replace('%', ''))
        vol = tr.xpath('./td[4]/text()').get()
        amount = tr.xpath('./td[5]/text()').get()
        flow_direction = tr.xpath('./td[6]/text()').get()
        raise_number = tr.xpath('./td[7]/text()').get()
        fall_number = tr.xpath('./td[8]/text()').get()
        avg_price = tr.xpath('./td[9]/text()').get()  # 均价
        lead_stock = tr.xpath('./td[10]/a/text()').get()

        industry['industry_name'] = name
        industry['industry_pct_change'] = pct_change
        industry['industry_detail_url'] = industry_detail_url
        industry['industry_vol'] = vol
        industry['industry_amount'] = amount
        industry['industry_flow_direction_amount'] = flow_direction
        industry['raise_number'] = raise_number
        industry['fall_number'] = fall_number
        industry['avg_price'] = avg_price
        industry['lead_stock'] = lead_stock

        match = re.search('http://q.10jqka.com.cn/thshy/detail/code/(\d+)', industry_detail_url)
        industry_code = match.group(1)
        industry['industry_code'] = industry_code

        industry_id = dataObj.insert_industry_only(industry)
        print('插入 ', industry_id)


def main():
    industrty_list_url = "https://q.10jqka.com.cn/thshy/index/field/199112/order/desc/page/{}/ajax/1/"
    # 目前只有2页
    for page in range(1, 3):
        url = industrty_list_url.format(page)
        print('crawl {} '.format(url))
        response = crawl(url)
        if response:
            parser(response)
        else:
            logger.info('请求失败')


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        send_message_via_wechat('{}异常'.format(__file__))
        logger.info(e)
