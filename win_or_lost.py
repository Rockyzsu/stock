# -*-coding=utf-8-*-
__author__ = 'Rocky'
import pandas as pd
import os
import tushare as ts
import datetime
def getCodeFromExcel(filename):
    #从excel表中获取代码, 并且补充前面几位000
    #获取股票数目
    df=pd.read_excel(filename)
    code_list = df[u'证券代码'].values
    quantity_list=df[u'股票余额'].values
    print type(code_list)
    print type(quantity_list)
    code=[]
    quantity=[]
    for i in range(len(code_list)):
        code.append(str(code_list[i]).zfill(6))
        quantity.append(quantity_list[i])

    return code,quantity

def calc(code,quantity):
    settlement =  df[df['code']==code]['settlement'].values

    percentage =  df[df['code']==code]['changepercent'].values
    #print percentage
    #settlement=df[df['code'==code]]['settlement'].values
    #percentage=df[df['code'==code].index]['changepercent'].values
    #返回四舍五入的结果
    return round(settlement[0]*percentage[0]*quantity*0.01,1)


def today_win_lost():
    filename_path=os.path.join(os.getcwd(),'data')
    filename=os.path.join(filename_path,'ownstock.xls')
    print filename
    code,quantity=getCodeFromExcel(filename)
    print "Code"
    print code
    print "Quantity"
    print quantity
    result=[]
    for i in range(len(code)):
        result.append(calc(code[i],quantity[i]))

    return result

def join_dataframel():

    result=today_win_lost()
    s=pd.DataFrame({u'当天贡献':result})
    #print s
    df=pd.read_excel(filename)
    new_df=df.join(s,how='right')
    return new_df

def save_to_excel():
    df=join_dataframel()
    save_name=os.path.join(path,today+"_win_lost_.xls")
    df.to_excel(save_name)

if __name__ == "__main__":
    path=os.path.join(os.getcwd(),'data')
    filename=os.path.join(path,'ownstock.xls')
    now=datetime.datetime.now()
    today=now.strftime('%Y-%m-%d')
    df=ts.get_today_all()
    save_to_excel()
