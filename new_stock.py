import aiohttp
import asyncio
import execjs
import threading
global pages
global count

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Host": "dcfm.eastmoney.com",
    "Pragma": "no-cache",
    "Referer": "http://data.eastmoney.com/xg/xg/default.html",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/69.0.3497.81 Chrome/69.0.3497.81 Safari/537.36",
}

home_url = 'http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=XGSG_LB&token=70f12f2f4f091e459a279469fe49eca5&st=purchasedate,securitycode&sr=-1&p={}&ps=50&js=var%20hsEnHLwG={{pages:(tp),data:(x)}}&rt=53512217'

loop = asyncio.get_event_loop()
lock = asyncio.Lock()
def parse_json(content):
    content += ';function getV(){return hsEnHLwG;}'
    ctx = execjs.compile(content)
    result = ctx.call('getV')
    return result


async def fetch(session,page):
    global pages
    global count
    async with session.get(home_url.format(page),headers=headers) as resp:
        content = await resp.text()

        try:
            js_content = parse_json(content)
            for stock_info in js_content['data']:
                securityshortname = stock_info['securityshortname']
                # print(securityshortname)
        except Exception as e:
            print(e)

        async with lock:
            count=count+1

        print(f'count:{count}')
        if count == pages:
            print('End of loop')
            loop.stop()



async def main():
    global pages
    global count
    count=0
    async with aiohttp.ClientSession() as session:
        async with session.get(home_url.format(1), headers=headers) as resp:

            content = await resp.text()
            js_data = parse_json(content)
            pages = js_data['pages']
            print(f'pages: {pages}')
            for page in range(1,pages+1):
                task = asyncio.ensure_future(fetch(session,page))

            await asyncio.sleep(1)


asyncio.ensure_future(main())
loop.run_forever()