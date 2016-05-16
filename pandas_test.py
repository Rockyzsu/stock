#-*-coding=utf-8-*-
#author: Rocky Chen
import pandas as pd
import numpy as np
#import matpl

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

base_case()