# -*- coding: utf-8 -*-
# @Time : 2021/4/20 12:54
# @File : danjuan_fund_data_analysis.py
# @Author : Rocky C@www.30daydo.com
# 蛋卷数据分析
import datetime
import sys
from collections import defaultdict
sys.path.append('..')
from configure.settings import DBSelector
from common.BaseService import BaseService
import pandas as pd


WEEK_DAY = -7 # 上一周的价格

class DanjuanAnalyser(BaseService):

    def __init__(self):
        super(DanjuanAnalyser, self).__init__('../log/Danjuan_analysis.log')


    def select_collection(self,current_date):
        '''
        根据日期选择数据库
        '''

        self.db = DBSelector().mongo(location_type='qq')
        doc = self.db['db_danjuan'][f'danjuan_fund_{current_date}']
        return doc

    def get_top_plan(self,collection,top=10):
        fund_dict = {}
        for item in collection.find({},{'holding':1}):
            plan_holding = item.get('holding',[]) # list
            for hold in plan_holding:
                name = hold['fd_name']
                if hold['percent']>0:
                    fund_dict.setdefault(name,0)
                    fund_dict[name]+=1
        fund_dict=list(sorted(fund_dict.items(),key=lambda x:x[1],reverse=True))[:top]
        return fund_dict


    def get_top_plan_percent(self,collection,top=10):
        fund_dict = {}
        for item in collection.find({},{'holding':1}):
            plan_holding = item.get('holding',[]) # list
            for hold in plan_holding:
                name = hold['fd_name']
                percent =hold['percent']
                fund_dict.setdefault(name,0)
                fund_dict[name]+=percent
        fund_dict=list(sorted(fund_dict.items(),key=lambda x:x[1],reverse=True))[:top]
        return fund_dict

    def start(self):

        today=datetime.datetime.now()
        last_week = today + datetime.timedelta(days=WEEK_DAY)
        last_week_str = last_week.strftime('%Y-%m-%d')
        # 因为没有执行上周的数据，用历史数据替代
        last_week_str = '2021-04-20' # 需要已经保存的库

        today_doc = self.select_collection(self.today)
        last_week_doc = self.select_collection(last_week_str)

        # 持有个数
        fund_dict = self.get_top_plan(today_doc,20)
        self.pretty(fund_dict,self.today,'count')

        old_fund_dict = self.get_top_plan(last_week_doc,20)
        self.pretty(old_fund_dict,last_week_str,'count')
        
        diff_set = self.new_fund(fund_dict,old_fund_dict)
        print('新增的基金入围')
        print(diff_set)

        # 按持有比例
        new_fund_percent = self.get_top_plan_percent(today_doc,20)
        old_fund_percent = self.get_top_plan_percent(last_week_doc,20)
        
        self.pretty(new_fund_percent,self.today,'percent')
        self.pretty(old_fund_percent,last_week_str,'percnet')

        # 清仓
        clean_fund = self.clear_warehouse_fund(today_doc,200)
        self.simple_display(clean_fund,self.today)

    def simple_display(self,data,date):
        for i in data:
            print(i)

        df = pd.DataFrame(data,columns=['fund','clear_num'])
        print(df.head(100))
        df.to_excel(f'clear_{date}.xlsx')

    def pretty(self,fund_dict,date,kind):
        df = pd.DataFrame(fund_dict,columns=['fund','holding_num'])
        print(df.head(100))
        df.to_excel(f'{date}-{kind}.xlsx')

    def new_fund(self,new_fund_dict,old_fund_dict):
        new_fund_list = list(map(lambda x: x[0], new_fund_dict))
        old_fund_list = list(map(lambda x: x[0], old_fund_dict))
        diff_set= set(old_fund_list)-set(new_fund_list)
        return diff_set

    def clear_warehouse_fund(self,collection,top):
        '''
        清仓的基金
        '''
        fund_dict = {}
        for item in collection.find({},{'holding':1}):
            plan_holding = item.get('holding',[]) # list
            for hold in plan_holding:
                name = hold['fd_name']
                percent =hold['percent']

                if percent>0:
                    continue
                fund_dict.setdefault(name,0)
                fund_dict[name]+=1
        fund_dict=list(sorted(fund_dict.items(),key=lambda x:x[1],reverse=True))[:top]
        return fund_dict


def main():
    app = DanjuanAnalyser()
    app.start()

if __name__ == '__main__':
    main()
