# 研报下载

import requests
import os
from parsel import Selector
import urllib.parse
def main():
    url = 'https://aigc.idigital.com.cn/djyanbao/'
    req = requests.get(url)
    resp = Selector(text=req.text)
    all_url = resp.xpath('//body//a/@href').getall()
    for sub_url in all_url:
        if sub_url.endswith('pdf'):
            full_url = url + sub_url
            # print(full_url)
            pdf_name = sub_url.split('/')[-1]
            pdf_name = urllib.parse.unquote(pdf_name)
            print(pdf_name)
            local_path = os.path.join(os.getcwd(), 'yanbao',pdf_name)
            if os.path.exists(local_path):
                print(f"File {pdf_name} already exists, skipping download.")
                continue
            try:
                pdf_resp = requests.get(full_url,headers={'User-Agent': 'Mozilla/5.0'})
                with open(local_path, 'wb') as f:
                    f.write(pdf_resp.content)
            except Exception as e:
                print(f"Error saving {pdf_name}: {e}")
                continue

if __name__ == "__main__":
    main()