# -*-coding=utf-8-*-
__author__ = 'Rocky'
import requests
class Strategy():
    def __init__(self):
        self.base_url='https://xueqiu.com/strategy/'
        self.headers={'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:33.0) Gecko/20100101 Firefox/33.0',
                      'Host':'xueqiu.com',
                      }


    def getData(self,page):
        url=self.base_url+str(page)
        #url='https://xueqiu.com/snowmart/push/stocks.json?product_id=19&page=3&count=5'
        resp=requests.get(url,headers=self.headers)
        print resp.status_code
        print resp.text



if __name__=='__main__':
    obj=Strategy()
    obj.getData(19)
