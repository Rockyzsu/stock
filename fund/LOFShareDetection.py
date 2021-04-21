# -*- coding: utf-8 -*-
# @Time : 2021/3/29 22:33
# @File : LOFShareDetection.py
# @Author : Rocky C@www.30daydo.com

# LOF 份额变动
import sys

sys.path.append('..')
from configure.settings import DBSelector
from LOF_Model import FundBaseInfoModel, ShareModel, Base
from sqlalchemy.orm import sessionmaker
from common.TushareUtil import TushareBaseUtil
from sqlalchemy import or_, and_
from datetime import datetime
import pandas as pd
from configure.settings import send_from_aliyun
from common.BaseService import BaseService

class FundDection(BaseService):
    def __init__(self):
        super(FundDection, self).__init__('../log/FundDetection.log')
        self.engine = self.get_engine()
        self.db_session = self.get_session()
        self.sess = self.db_session()
        self.ts_util = TushareBaseUtil()

    def get_engine(self):
        return DBSelector().get_engine('db_stock')

    def create_table(self):
        # 初始化数据库连接:
        Base.metadata.create_all(self.engine)  # 创建表结构

    def get_session(self):
        return sessionmaker(bind=self.engine)

    def start(self):
        query_result_str,has_data = self.query_big_volatility_share()

        if has_data:
            title=f'{self.today} LOF/ETF 申购波动数据'
            print(title)
            print(query_result_str)
            send_from_aliyun(title,content=query_result_str)
        else:
            self.logger.info(f'今天{self.today}没有数据')

    def query_big_volatility_share(self):
        day = 0  # 前x天 ，天 ，0 即使昨天和前天的数据比较
        PERCENT = 10 # 偏离 百分比
        category_list = ["LOF","ETF"]

        yesterday = self.ts_util.get_last_trade_date()  # 最新的一天
        yesterday = self.ts_util.date_convertor(yesterday)
        lastday_of_yesterday = self.ts_util.get_trade_date()[-3 - day]  # 上一天
        lastday_of_yesterday = self.ts_util.date_convertor(lastday_of_yesterday)

        string_arg = ''
        has_data = False
        for category in category_list:
            # print(category)
            # print('#' * 10)
            string_arg+=f'############ {category} ###############\n\n'
            lastest_lofs = self.sess.query(FundBaseInfoModel.name, FundBaseInfoModel.code, ShareModel.share,
                                           ShareModel.date).join(ShareModel).filter(
                FundBaseInfoModel.category == category).filter(
                or_(ShareModel.date == yesterday, ShareModel.date == lastday_of_yesterday)).all()

            current_df = pd.DataFrame(lastest_lofs)

            current_df['date'] = current_df['date'].astype(str)
            current_df['share'] = current_df['share'].astype(float)
            current_df['code'] = current_df['code'].astype(str)
            current_df['name'] = current_df['name'].astype(str)

            for code, sub_df in current_df.groupby('code'):
                # 按照code分组，把前后两个值做差值
                yesterday_share = sub_df[sub_df['date'] == yesterday]
                lastday_of_yesterday_share = sub_df[sub_df['date'] == lastday_of_yesterday]

                if len(yesterday_share) > 0 and len(lastday_of_yesterday_share) > 0:
                    yesterday_share_num = yesterday_share['share'].to_list()[0]
                    lastday_of_yesterday_num = lastday_of_yesterday_share['share'].to_list()[0]
                    diff = (yesterday_share_num - lastday_of_yesterday_num) * 1.00 / lastday_of_yesterday_num * 100.00
                    diff = round(diff, 2)
                    if abs(diff) > PERCENT:

                        has_data = True # 有数据则发送邮件

                        print(yesterday_share['name'].to_list()[0], yesterday_share['code'].to_list()[0],
                              yesterday_share_num, lastday_of_yesterday_num, lastday_of_yesterday, diff)
                        string = self.formator(category,yesterday_share['name'].to_list()[0], yesterday_share['code'].to_list()[0],
                                      yesterday_share_num, lastday_of_yesterday_num, lastday_of_yesterday, diff)
                        # print(string)
                        string_arg+=string+'\n'
            string_arg+='\n'

        # print(string_arg)
        return string_arg,has_data

    def formator(self, *args):
        string = '{} {} {} {}万份 {}万份 {} {}%\n'.format(*args)

        return string


def main():
    app = FundDection()
    app.start()


if __name__ == '__main__':
    main()
