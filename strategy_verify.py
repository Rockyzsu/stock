# -*-coding=utf-8-*-
__author__ = 'Rocky'
import requests,time,re
from lxml import etree
from pandas import DataFrame
import sqlite3
# -*-coding=utf-8-*-
__author__ = 'Rocky'
import sqlite3



def create_table(strategy):
    dbname='stragety_%d.db' %strategy
    conn = sqlite3.connect(dbname)
    try:
        create_tb_cmd='''
            CREATE TABLE IF NOT EXISTS STRATEGY('日期' TEXT,'代码' TEXT,'股票' TEXT,'买入时间' TEXT,'盈亏' TEXT,'买入价格' TEXT,'当前价格' TEXT,'描述' TEXT);
            '''

        conn.execute(create_tb_cmd)
        conn.commit()
        conn.close()
        print "create table successful"
    except:
        print "Create table failed"
        return False




def insert(strategy,date_time,code,name,trigger_time,profit,trigger_price,current,desc):
    dbname='stragety_%d.db' %strategy
    conn = sqlite3.connect(dbname)
    print "open database passed"
        #conn.text_factory = str
    cmd="INSERT INTO STRATEGY ('日期','代码', '股票','买入时间' ,'盈亏' ,'买入价格' ,'当前价格','描述' ) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s');" %(date_time,code,name,trigger_time,profit,trigger_price,current,desc)

    conn.execute(cmd)
    conn.commit()
    conn.close()
    print "Insert successful"

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
        self.headers['Referer']='https://xueqiu.com/strategy/%s' %str(strategy)
        self.headers['X-Requested-With']='XMLHttpRequest'
        self.headers['DNT']='1'
        self.headers['Cookie']='s=7e18j5feh8; xq_a_token=720138cf03fb8f84ecc90aab8d619a00dda68f65; xq_r_token=0471237c52a208e16ce2d756fe46219b8066604d; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1489555354; __utma=1.842959324.1489555354.1489555354.1489555354.1; __utmc=1; __utmz=1.1489555354.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); u=301489555354143; Hm_lvt_1db88642e346389874251b5a1eded6e3=1489555354; aliyungf_tc=AQAAAHCnVki7tAwAAzISy6/ldZVhH55k'
        data={'product_id':strategy,'page':page,'count':5}
        resp=requests.get(url,params=data,headers=self.headers)

        return resp.json()

    def dataStore_SQLite(self,strategy,page):
        json_data=self.getStock(strategy,page)
        #print json_data
        if len(json_data)==0:

            return 0
        items=json_data['items']
        if len(items)==0:
            return 0

        create_table(strategy)
        #print items

        for item in items:
            desc=item['desc'].encode('utf-8')
            current=item['current']
            trigger_time=item['trigger_time']
            name=item['name'].encode('utf-8')
            trigger_price=item['trigger_price']
            code=item['symbol'].encode('utf-8')
            profit=item['change_percent']*100
            #print profit
            date_time=item['trigger_time']
            '''
            print type(desc)
            print type(current)
            print type(trigger_price)
            print type(trigger_time)
            print type(code)
            print type(profit)
            print type(date_time)
            print type(name)
            '''
            insert(strategy,date_time,code,name,trigger_time,profit,trigger_price,current,desc)

    def dataFilter(self,strategy,page):
        json_data=self.getStock(strategy,page)
        items=json_data['items']
        colums_dict={u'current': '', u'name': '', u'trigger_price': '', u'symbol': '', u'status_id': '', u'trigger_time': '', u'is_new': '', u'change_percent': '', u'flag': '', u'reply_count': '', u'target': '', u'desc': ''}

        df_total=DataFrame(colums_dict,index=['0'])
        for item in items:
            #print item
            df=DataFrame(item,index=['0'])
            print df
            df_total=df_total.append(df,ignore_index=True)

            '''
            current: 目前价格
            trigger_price: 入选价
            change_percent: 盈亏比例 小数，非百分比
            desc: 描述 帖子

            '''

        df_total.to_excel('stragety.xls')

    def DataDup(self,strategy):
        dbname='stragety_19_dadan.db'
        conn=sqlite3.connect(dbname)
        cmd='delete from STRATEGY where rowid not in (select max(rowid) from STRATEGY group by 代码);'
        conn.execute(cmd)
        conn.commit()
        conn.close()

    def loops(self):

        for i in range(1,70):
                for j in range(20):
                    print "Strategy %d" %i
                    status=self.dataStore_SQLite(i,j)
                    if status==0:
                        break
                    time.sleep(5)

if __name__=='__main__':
    obj=Strategy()
    #obj.getData(1)
    #obj.getStock()
    #obj.loops()
    obj.DataDup(0)
