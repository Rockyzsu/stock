# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''

#查询个股
import tushare as ts
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from threading import Thread
from multiprocessing import Pool,Queue,Process,Manager
import multiprocessing
multiprocessing.freeze_support()

class CheckStock():
    def __init__(self):
        #self.id=id
        self.base = pd.read_csv('bases.csv', dtype={'code': np.str})

        '''
        if len(self.id)!=6:
            print("Wrong stock code")
            exit()
        '''


    def multi_thread(self):

        with open('stock_list.txt') as f:
            stock_list=f.readlines()

        ratio_list=[]
        for i in stock_list:
            i=i.strip()
            ratio_list.append(self.get_info(i))
        #print(ratio_list)
        return ratio_list

    def get_info(self,id):
        print(id)
        try:
            df=ts.get_today_ticks(id)
            print('len of df ',len(df))
            #print(df)
            if len(df)==0:
                print("Pause of exchange")
                return id,'pause'
        except Exception as e:
            print(e)
            print("ERROR")
            return id,'pause'

        '''
        print('\n')
        max_p=df['price'].max()
        print(max_p)
        min_p=df['price'].min()
        print(min_p)
        #print(df)
        '''
        buy= df[df['type']=='买盘']['volume'].sum()
        #print('buy:',buy)
        sell =df[df['type']=='卖盘']['volume'].sum()
        #print('sell: ',sell)
        neutral= df[df['type']=='中性盘']['volume'].sum()
        #print('neutral: ',neutral)
        #最后一个是开盘数据
        start=df[-1:]
        vol_0=start['volume'].sum()
        #print('start')
        #print(start)
        total=buy+sell+neutral+vol_0

        sum_all=df['volume'].sum()

        #print(total)
        #print(sum_all)

        ratio=round((buy-sell)*1.00/sell*100,2)
        #print("buy/sell ratio: ",ratio)
        return id,ratio
        '''
        df['price'].plot()
        plt.grid()

        plt.show()
        '''



    #类中不能多进程
    def multi_process(self):
        stock_list=[]
        with open('stock_list.txt') as f:
            stock_list=f.readlines()
        #print(stock_list)
        stock_list=map(lambda x:x.strip(),stock_list)
        #print(stock_list)
        '''
        p=Pool(len(stock_list))
        result=p.map(self.get_info,stock_list)
        p.close()
        p.join()
        '''
        p=Pool(len(stock_list))
        #p_list=[]
        result=[]
        for i in stock_list:
            t=p.apply_async(self.get_info,args=(i,))
            #p_list.append(Process(target=self.get_info,args=(i)))
            result.append(t)
        p.close()
        p.join()
        print(result)
        '''
        for j in p_list:
            j.start()
        for k in p_list:
            k.join()
        '''


        print(result)

    def show_name(self):
        #self.all=ts.get_stock_basics()
        #self.bases_save=ts.get_stock_basics()

        #self.bases_save.to_csv('bases.csv')

        stock_list=self.multi_thread()
        for st in stock_list:

            print("code: ",st[0])
            name=self.base[self.base['code']==st[0]]['name'].values[0]
            print('name: ',name)
            print("ratio: ",st[1])
            if st[1]>30:
                print("WOW, more than 30")
            print('\n')

    def sinle_thread(self,start,end):
        for i in range(start,end):
            id,ratio=self.get_info(self.all_code[i])
            if ratio =='pause':
                continue
            if ratio>30:
                print(self.base[self.base['code']==id]['name'].values[0],' buy more than 30 percent')

    def scan_all(self):
        self.all_code=self.base['code'].values
        thread_num=500
        all_num=len(self.all_code)
        each_thread=all_num/thread_num
        #print(type(all_code))
        thread_list=[]
        for i in range(thread_num):
            t=Thread(target=self.sinle_thread,args=(i*each_thread,(i+1)*each_thread))
            thread_list.append(t)

        for j in thread_list:
            j.start()

        for k in thread_list:
            k.join()


    def monitor(self):
        ratio_list=self.multi_thread()
        for js in ratio_list:
            if js[1]>30:
                print(js[0])




def sub_process_ratio(i,q):
    print("Start")
    try:
        df=ts.get_today_ticks(i)
        #print('len of df ',len(df))
        #print(df)
        if len(df)==0:
            print("Pause of exchange")
            return i,'pause'
    except Exception as e:
        print(e)
        print("ERROR")
        return id,'pause'

    '''
    print('\n')
    max_p=df['price'].max()
    print(max_p)
    min_p=df['price'].min()
    print(min_p)
    #print(df)
    '''
    buy= df[df['type']=='买盘']['volume'].sum()
    #print('buy:',buy)
    sell =df[df['type']=='卖盘']['volume'].sum()
    #print('sell: ',sell)
    neutral= df[df['type']=='中性盘']['volume'].sum()
    #print('neutral: ',neutral)
    #最后一个是开盘数据
    start=df[-1:]
    vol_0=start['volume'].sum()
    #print('start')
    #print(start)
    total=buy+sell+neutral+vol_0

    sum_all=df['volume'].sum()

    #print(total)
    #print(sum_all)

    ratio=round((buy-sell)*1.00/sell*100,2)
    #print("buy/sell ratio: ",ratio)
    s= [i,ratio]
    print(s)
    q.put(s)

def testcase1(i,j,q):
    print(i,j)
    q.put(i)

def multi_process():
    #stock_list=[]
    with open('stock_list.txt') as f:
        stock_list=f.readlines()
    #print(stock_list)
    stock_list=map(lambda x:x.strip(),stock_list)
    print(stock_list)

    '''
    p=Pool(len(stock_list))
    result=p.map(self.get_info,stock_list)
    p.close()
    p.join()
    '''
    p=Pool(len(stock_list))
    #p_list=[]
    result=[]
    manager=Manager()
    q=manager.Queue()
    #p1=Pool(8)
    #q1=Queue()
    for i in stock_list:
        #print(i)
        p.apply_async(sub_process_ratio,args=(i,q))
        #p1.apply_async(testcase1,args=(i,i,q1))
        #p_list.append(Process(target=self.get_info,args=(i)))
        #result.append(t)
    p.close()
    p.join()
    #print(result)

    while q.empty()==False:
        print('get')
        print(q.get())


if __name__=="__main__":
    #obj=CheckStock()
    #obj.get_info('000693')
    #obj.multi_thread()
    #obj.show_name()
    #obj.monitor()
    #obj.scan_all()
    #obj.multi_process()
    multi_process()