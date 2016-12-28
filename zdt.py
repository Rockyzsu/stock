#-*- coding=utf-8 -*-
__author__ = 'Rocky'
#每天的涨跌停
#url=http://stock.jrj.com.cn/tzzs/zdtwdj/zdforce.shtml
import urllib2,re,time,xlrd,xlwt
class GetZDT():
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)"
        self.today=time.strftime("%Y%m%d")
        print self.today
        #self.url='http://stock.jrj.com.cn/tzzs/zdtwdj/zdforce.shtml'
        #self.url='http://home.flashdata2.jrj.com.cn/limitStatistic/ztForce/20161201.js'
        self.url='http://home.flashdata2.jrj.com.cn/limitStatistic/ztForce/'+self.today+".js"
        self.host="home.flashdata2.jrj.com.cn"
        self.reference="http://stock.jrj.com.cn/tzzs/zdtwdj/zdforce.shtml"
        self.header = {"User-Agent": self.user_agent,"DNT":"1","Host":self.host,"Referer":self.reference}
        #self.getData()

    def getData(self):
        req=urllib2.Request(headers=self.header,url=self.url)
        resp=urllib2.urlopen(req)
        content= resp.read()
        return content

    def fetchData(self):
        p=re.compile(r'"Data":(.*)};',re.S)
        #temp_content=open("zdt.html",'r').read()
        #print temp_content
        content=self.getData()
        result=p.findall(content)
        t1= result[0]
        t2=list(eval(t1))
        #print type(t2)
        #print t2
        '''
        for i in t2:
            for j in i:
                print j
        '''
        return t2


    def storeData(self):
        filename=self.today+".txt"
        data=self.fetchData()
        '''
        f=open(filename,'w')
        for i in data:
            for j in i:
                print j
                print type(j)
                f.write(str(j)+'; ')

            f.write('\n')
        '''
        #f=open('20161201.txt','w')
        #f.write(str(data))
        #f.close()
        self.save_excel(self.today,data)

    #2016-12-27 to do this
    def save_excel(self,date,data):
        #data is list type
        w=xlwt.Workbook(encoding='gbk')
        ws=w.add_sheet(date)
        excel_filenme=date+".xls"
        #sheet=open_workbook(excel_filenme)
        #table=wb.sheets()[0]
        xf=0
        ctype=1
        rows=len(data)
        point_x=1
        point_y=0
        print "Rows:%d" %rows
        for row in data:
            rows=len(data)
            cols=len(row)
            point_y=0
            for col in row:
                #print col
                #table.put_cell(row,col,)
                print col
                ws.write(point_x,point_y,col)
                print "[%d,%d]" %(point_x,point_y)
                point_y=point_y+1

            point_x=point_x+1

        w.save(excel_filenme)

if __name__=='__main__':

    #today=time.strftime("%Y-%m-%d")
    #print today
    #print type(today)
    obj=GetZDT()
    obj.storeData()

