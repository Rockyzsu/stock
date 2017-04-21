# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
获取雪球的策略 2017-03-21
'''
import requests,time,re,os
from lxml import etree
from pandas import DataFrame
import sqlite3
# -*-coding=utf-8-*-
__author__ = 'Rocky'
import sqlite3,sys,cookielib,datetime



def create_table(strategy):
    work_path=os.path.join(os.getcwd(),'data')

    if os.path.exists(work_path)==False:
        os.mkdir(work_path)

    dbname='stragety_%d.db' %strategy
    dbname=os.path.join(work_path,dbname)
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
    work_path=os.path.join(os.getcwd(),'data')

    if os.path.exists(work_path)==False:
        os.mkdir(work_path)

    dbname='stragety_%d.db' %strategy
    dbname=os.path.join(work_path,dbname)
    try:
        conn = sqlite3.connect(dbname)
        print "open database passed"
            #conn.text_factory = str
        cmd="INSERT INTO STRATEGY ('日期','代码', '股票','买入时间' ,'盈亏' ,'买入价格' ,'当前价格','描述' ) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s');" %(date_time,code,name,trigger_time,profit,trigger_price,current,desc)

        conn.execute(cmd)
        conn.commit()
        conn.close()
        print "Insert successful"
    except:
        print "Insert Failed"

class Strategy():

    def __init__(self):
        self.base_url='https://xueqiu.com/strategy/'
        self.headers={'User-Agent':'Mozilla/5.0 (Windows NT 5.1; rv:33.0) Gecko/20100101 Firefox/33.0',
                      'Host':'xueqiu.com',
                      }
        self.headers['X-Requested-With']='XMLHttpRequest'
        self.headers['DNT']='1'
        self.s=requests.session()


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

        data_up={'product_id':strategy,'page':page,'count':5}
        self.s.get('https://xueqiu.com',headers=self.headers)

        resp=self.s.get(url,params=data_up,headers=self.headers)
        #time.sleep(20)
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

        for item in items:
            desc=item['desc'].encode('utf-8')
            current=item['current']
            d_time=datetime.datetime.fromtimestamp(item['trigger_time']*1.0/1000)
            str_time=d_time.strftime('%Y-%m-%d %H:%M')

            #trigger_time=datetime.datetime.fromtimestamp(item['trigger_time']*1.0/1000)
            trigger_time=str_time
            name=item['name'].encode('utf-8')
            trigger_price=item['trigger_price']
            code=item['symbol'].encode('utf-8')
            profit=item['change_percent']*100.0
            #print profit
            date_time=str_time
            #date_time=time.ctime(item['trigger_time']*1.0/1000)
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
        work_path=os.path.join(os.getcwd(),'data')

        if os.path.exists(work_path)==False:
            os.mkdir(work_path)

        dbname='stragety_%d.db' %strategy
        dbname=os.path.join(work_path,dbname)

        try:
            conn=sqlite3.connect(dbname)
            cmd='delete from STRATEGY where rowid not in (select max(rowid) from STRATEGY group by 代码);'
            conn.execute(cmd)
            time.sleep(1)
            conn.commit()
            time.sleep(1)
            conn.close()
            time.sleep(1)
        except:
            print "remove failed on ",strategy

    def loops(self):
        for i in range(1,70):
                for j in range(20):
                    print "Strategy %d" %i
                    status=self.dataStore_SQLite(i,j)
                    if status==0:
                        break
                    time.sleep(2)

    def monitor(self,strategy):
        print "monitor"
        print "#"*20
        print '\n'
        for i in range(10):
            json_data=self.getStock(strategy,i)
            items=json_data['items']
            for item in items:
                print '\n\n'
                d_time=datetime.datetime.fromtimestamp(item['trigger_time']*1.00/1000)
                str_time=d_time.strftime('%Y-%m-%d %H:%M')
                print u'买入时间 ',str_time
                #print u'买入时间 ',time.ctime(item['trigger_time']*1.00/1000)
                print u'当前价格 ',item['current']
                print item['name']
                print u'买入价格 ',item['trigger_price']
                print u'目前盈亏 ',float(item['change_percent'])*100.0
                print item['desc']

            time.sleep(1)

def main():

    selection=input("Select option :\n"
                    "1.\tMonitor the stragegy \n"
                    "2.\tStore to Database\n"
                    "3.\tRemove duplicate items\n")

    obj=Strategy()
    if selection==1:
        strategy=input('Strategy:')
        obj.monitor(strategy)

    elif selection ==2:
        obj.loops()
    elif selection==3:
        for i in range(1,60):
            obj.DataDup(i)


if __name__=='__main__':
    main()
