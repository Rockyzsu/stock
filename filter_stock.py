# -*-coding=utf-8-*-
__author__ = 'Rocky'
import tushare as ts
import os
import pandas as pd
import pandas
pandas.set_option('display.max_rows',None)
class Filter_Stock():

    def __init__(self):
        current=os.getcwd()
        work_space=os.path.join(current,'data')
        if os.path.exists(work_space) ==False:
            os.mkdir(work_space)
        os.chdir(work_space)
        print os.getcwd()

    def get_location(self,loc):
        df=ts.get_area_classified()
        print df


    def get_ST(self):
        #暂停上市
        zt=ts.get_suspended()
        print zt

        #终止上市
        zz=ts.get_terminated()
        print zz

    def get_achievement(self):

        fc=ts.forecast_data(2016,4)

        print fc

if __name__=='__main__':
    obj=Filter_Stock()
    #obj.get_ST()
    #obj.get_achievement()
    obj.get_location(u'深圳')