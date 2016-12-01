# -*-coding=utf-8-*-
__author__ = 'Rocky'
#每天的涨跌停
#url=http://stock.jrj.com.cn/tzzs/zdtwdj/zdforce.shtml
import urllib2
class GetZDT():
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.header = {"User-Agent": self.user_agent}
        self.url='http://stock.jrj.com.cn/tzzs/zdtwdj/zdforce.shtml'
        self.url='http://home.flashdata2.jrj.com.cn/limitStatistic/ztForce/20161201.js'

    def getData(self):
        req=urllib2.Request(headers=self.header,url=self.url)
        resp=urllib2.urlopen(req)
        print resp.read()



if __name__=='__main__':
    obj=GetZDT()
    obj.getData()

