import time

import aiohttp
import asyncio
import execjs
global pages
global count
import sys
sys.path.append('..')
from configure.util import read_web_headers_cookies
from configure.settings import DBSelector

headers,_ = read_web_headers_cookies('ttjj',headers=True,cookies=False)
home_url = 'http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=XGSG_LB&token=70f12f2f4f091e459a279469fe49eca5&st=purchasedate,securitycode&sr=-1&p={}&ps=50&js=var%20hsEnHLwG={{pages:(tp),data:(x)}}&rt=53512217'

loop = asyncio.get_event_loop()
# lock = asyncio.Lock()

mongo_client = DBSelector().mongo(location_type='qq',async_type=True)
# mongo_client = DBSelector().mongo(location_type='qq',async_type=False)
collection = mongo_client['db_stock']['new_stock_ttjj']

def parse_json(content):
    content += ';function getV(){return hsEnHLwG;}'
    ctx = execjs.compile(content)
    result = ctx.call('getV')
    return result

async def Aupdate_data(data):
    code = data['securitycode']
    found =  await collection.find_one({'securitycode':code})
    if not found:
        await collection.insert_one(data)
    print(code)

def update_data(data):
    code = data['securitycode']
    found =  collection.find_one({'securitycode':code})
    if not found:
        collection.insert_one(data)
        print('插入成功')
    print(code)

async def fetch(session,page):
    # global pages
    # global count
    async with session.get(home_url.format(page),headers=headers) as resp:
        content = await resp.text()

        try:
            js_content = parse_json(content)
            for stock_info in js_content['data']:
                securityshortname = stock_info['securityshortname']

                print(securityshortname)
                await Aupdate_data(stock_info)
        except Exception as e:
            print(e)

        # async with lock:
        #     count=count+1

        # print(f'count:{count}')
        # if count == pages:
        #     await asyncio.sleep(20)
        #     print('End of loop')
        #     loop.stop()



async def main():
    # global pages
    # global count
    # count=0
    start = time.time()
    async with aiohttp.ClientSession() as session:
        async with session.get(home_url.format(1), headers=headers) as resp:

            content = await resp.text()
            js_data = parse_json(content)
            pages = js_data['pages']
            tasks =[]
            for page in range(1,pages+1):
                task = asyncio.create_task(fetch(session,page))
                # tasks.append(fetch(session,page))
                tasks.append(task)

            await asyncio.gather(*tasks)

    print(f'time used {time.time()-start}')
# loop = asyncio.get_event_loop()
loop.run_until_complete(main())
# asyncio.run(main())
# loop.run_forever()