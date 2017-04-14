# -*-coding=utf-8-*-
__author__ = 'Rocky'
import pandas as pd
import matplotlib.pyplot as plt
import os
#图形显示某一天的涨跌幅分布
def count_up_down(filename):
    total=[]
    df=pd.read_excel(filename)

    count= len(df[(df['changepercent']>=-10.2) & (df['changepercent']<-9)])
    total.append(count)
    for i in range(-9,9,1):
        count= len(df[(df['changepercent']>=i*1.00) & (df['changepercent']<((i+1))*1.00)])
        total.append(count)
    count= len(df[(df['changepercent']>=9)])
    total.append(count)
    print total
    df_figure=pd.Series(total,index=[range(-10,10)])
    print df_figure
    fg=df_figure.plot(kind='bar',table=True)
    plt.show(fg)

if __name__=='__main__':
    foler=os.path.join(os.getcwd(),'data')
    filename='2017-04-13_all_.xls'
    full_path=os.path.join(foler,filename)
    count_up_down(full_path)