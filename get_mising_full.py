#-*-coding=utf-8-*-

import tushare as ts
import os
import pandas as pd
import numpy as np
import datetime
pd.set_option('display.max_rows',None)
def getTotal():
    path=os.path.join(os.getcwd(),'data')
    os.chdir(path)

    all=pd.read_csv('bases.csv',dtype={'code':np.str})
    #print all

    all_code=all['code'].values
    #print all_code

    lists=[]
    for i in all_code:
        df=ts.get_k_data(i,start='2017-07-17',end='2017-07-17')
        lists.append(df)

    all_df=pd.DataFrame(lists)
    print all_df
    all_df.to_csv('2017-all.csv',encoding='gbk')
    all_df.to_excel('2017-excel.xls')




getTotal()
