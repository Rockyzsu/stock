# -*-coding=utf-8-*-
__author__ = 'Rocky'
import requests,time,re
from lxml import etree
class Strategy():
    def __init__(self):
        self.base_url='https://xueqiu.com/strategy/'
        self.headers={'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:33.0) Gecko/20100101 Firefox/33.0',
                      'Host':'xueqiu.com',
                      }


    def getData(self,page):
        url=self.base_url+str(page)
        resp=requests.get(url,headers=self.headers)
        print resp.status_code
        print resp.text


    def show_strategy(self):
        Status_Code=200
        base_url='https://xueqiu.com/strategy/'

        for i in range(100):
            no_strategy=0
            url=base_url+str(i)
            resp=requests.get(url,headers=self.headers)
            if resp.status_code==200:

                content=resp.text
                tree=etree.HTML(content)
                all_contnet=tree.xpath('//div[@class="detail-bd"]')
                print tree.xpath('//title/text()')[0]
                content_str=[]
                temp=[]
                p=re.compile(u'待定')
                for j in all_contnet:
                    s= j.xpath('string(.)')
                    temp.append(s)
                    if p.findall(s):
                        no_strategy=1

                if no_strategy==0:
                    print '%d has strategy' %i
                    for it in temp:
                        print it
            time.sleep(10)

    def getStock(self,strategy,page):
        url='https://xueqiu.com/snowmart/push/stocks.json?product_id=%s&page=%s&count=5' %(str(strategy),str(page))
        url='https://xueqiu.com/snowmart/push/stocks.json?product_id=19&page=3&count=5'
        #url='https://xueqiu.com/strategy/'
        self.headers['Referer']='https://xueqiu.com/strategy/19'


        self.headers['X-Requested-With']='XMLHttpRequest'
        self.headers['DNT']='1'
        #self.headers['Cookie']='s=7e18j5feh8; xq_a_token=720138cf03fb8f84ecc90aab8d619a00dda68f65; xq_r_token=0471237c52a208e16ce2d756fe46219b8066604d; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1489555354; __utma=1.842959324.1489555354.1489555354.1489555354.1; __utmc=1; __utmz=1.1489555354.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); u=301489555354143; Hm_lvt_1db88642e346389874251b5a1eded6e3=1489555354; aliyungf_tc=AQAAAHCnVki7tAwAAzISy6/ldZVhH55k'
        #need cookies
        data={'product_id':strategy,'page':page,'count':5}

        #print self.headers
        return resp.json()
        s=session.get('http://xueqiu.com',headers=self.headers)

        print self.headers
        resp=session.get(url,headers=self.headers,params=data).text
        print resp

    def dataFilter(self,strategy,page):
        json_data=self.getStock(strategy,page)
        items=json_data['items']
        for item in items:
            print item['name'],
            print item['trigger_price'],
            print item['trigger_time'],
            print item['desc']



    def loops(self):
        for i in range(1,5):
            self.dataFilter(19,i)

'''
Remote Address:118.178.213.44:443
Request URL:https://xueqiu.com/snowmart/push/stocks.json?product_id=19&page=3&count=5
Request Method:GET
Status Code:200 OK
Request Headersview source
Accept:*/*
Accept-Encoding:gzip,deflate
Accept-Language:en-US,en;q=0.8,zh;q=0.6
Connection:keep-alive
Cookie:s=7e18j5feh8; xq_a_token=720138cf03fb8f84ecc90aab8d619a00dda68f65; xq_r_token=0471237c52a208e16ce2d756fe46219b8066604d; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1489555354; __utma=1.842959324.1489555354.1489555354.1489555354.1; __utmc=1; __utmz=1.1489555354.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); u=301489555354143; Hm_lvt_1db88642e346389874251b5a1eded6e3=1489555354; aliyungf_tc=AQAAAHCnVki7tAwAAzISy6/ldZVhH55k
DNT:1
Host:xueqiu.com
Referer:https://xueqiu.com/strategy/19
User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.120 Chrome/37.0.2062.120 Safari/537.36
X-Requested-With:XMLHttpRequest
Query String Parametersview sourceview URL encoded
product_id:19
page:3
count:5
Response Headersview source
Cache-Control:private, no-store, no-cache, must-revalidate, max-age=0
Connection:keep-alive
Content-Encoding:gzip
Content-Type:application/json;charset=UTF-8
Date:Thu, 16 Mar 2017 07:47:43 GMT
P3P:"CP="IDC DSP COR ADM DEVi TAIi PSA PSD IVAi IVDi CONi HIS OUR IND CNT""
Server:openresty/1.11.2.1
Strict-Transport-Security:max-age=31536000
Trace-Id:ce2c5fc01eca5b7f
Transfer-Encoding:chunked
Vary:Accept-Encoding
product_id:19
page:3
count:5
'''

if __name__=='__main__':
    obj=Strategy()
    #obj.getData(1)
    #obj.getStock()
    obj.loops()
