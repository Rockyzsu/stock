import datetime
import requests
from fire import Fire
import demjson
import sys
sys.path.append('..')
from configure.settings import DBSelector

def crawl(url):

    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh,en-US;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'https://www.sse.com.cn/',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Cookie': 'gdp_user_id=gioenc-0025a135%2Ca10b%2C57a8%2C8753%2Ce792c89cddec; ba17301551dcbaf9_gdp_session_id=96dfc8ec-8150-441f-94e8-ec3e9594620d; ba17301551dcbaf9_gdp_session_id_sent=96dfc8ec-8150-441f-94e8-ec3e9594620d; ba17301551dcbaf9_gdp_sequence_ids={%22globalKey%22:21%2C%22VISIT%22:3%2C%22PAGE%22:3%2C%22VIEW_CLICK%22:17}; JSESSIONID=6CC35D01776224F3199C94FCB93CB177'
    }

    response = requests.get(url, headers=headers)

    # print(response.text)
    js_data = response.text.replace('jsonpCallback45859518(', '').rstrip(');')
    data = demjson.decode(js_data)
    # print(data)
    parse_data(data)


def get_history_data():
    for year in range(2013, 2026):

        month = f'{year}12'
        print(month)
        url = "https://query.sse.com.cn//commonQuery.do?jsonCallBack=jsonpCallback45859518&sqlId=COMMON_SSE_TZZ_M_ALL_ACCT_C&isPagination=false&MDATE={}".format(month)
        js_data = crawl(url)
        if js_data:
            parse_data(js_data)

client = DBSelector().mongo(location_type='qq')
doc =client['db_stock']['securities_account']
doc.create_index([('month',1)],unique=True)

def dump_mongodb(item):
    _item = item
    _item['month']=item['TERM']
    del _item['MDATE']
    del _item['TERM']
    
    for key in _item:
        
        if key=='month':
            continue

        try:
            _item[key] = float(_item[key])
        except:
            pass

    try:
        doc.insert_one(_item)
    except Exception as e:
        print(e)

def parse_data(js_data):
    open_account_list = js_data['result']
    for item in open_account_list:
        # print(item)
        total = item['TOTAL']
        term = item['TERM']
        total = float(total)
        if total>0:
            try:
                term = float(term)
            except:
                continue
            print(f'{term} {total}')
            dump_mongodb(item)

def main(history=False):

    if history:
        get_history_data()
    else:
        last_month = datetime.datetime.now() - datetime.timedelta(days=30)
        last_month = last_month.strftime('%Y%m')
        print(f'current year: {last_month}')


        url = "https://query.sse.com.cn//commonQuery.do?jsonCallBack=jsonpCallback45859518&sqlId=COMMON_SSE_TZZ_M_ALL_ACCT_C&isPagination=false&MDATE={}".format(last_month)
        crawl(url)


if __name__ == '__main__':
    Fire(main)
