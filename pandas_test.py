#-*-coding=utf-8-*-
#author: Rocky Chen
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def base_case():


    dates = pd.date_range("20160516",periods=5)
    print dates

    df=pd.DataFrame(np.random.randn(5,5),index = dates,columns=list("ABCDE"))
    print df
    print df.describe()
    print df.dtypes
    print "Check the head 5"
    print df.head()

    print "check tail 5"
    print df.tail()

    print df.index
    print df.columns

    print df.T

    print df['B']
    print df[0:2]
    print df.loc['20160517':'20160519','A':'C']
    ts= pd.Series(np.random.randn(1000),index=pd.date_range('1/1/2000',periods=1000))
    ts=ts.cumsum()
    print "*"
    print ts.plot()

    df_11=pd.DataFrame(np.random.randn(1000,4),index=ts.index,columns=['A','B','C','D'])
    df_11 =df-df_11.cumsum()
    plt.figure()
    df_11.plot()

base_case()