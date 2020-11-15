__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''

import datetime
import time
import tushare as ts
import os
from settings import DBSelector,DATA_PATH
import pandas as pd
from BaseService import BaseService

# 获取市场全貌

class BasicMarket(BaseService):

    def __init__(self,logpath='log/collect_data.log'):
        super(BasicMarket, self).__init__(logpath)
        work_space=DATA_PATH
        if os.path.exists(work_space) ==False:
            os.mkdir(work_space)
        os.chdir(work_space)

        self.today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.daily_engine = DBSelector().get_engine('db_daily','qq')

    def daily_market(self):
        df = ts.get_today_all()
        try:
            df.to_sql(self.today,self.daily_engine,if_exists='replace')
        except Exception as e:
            self.logger.info(e)
        else:
            self.logger.info("Save {} data to MySQL".format(self.today))

    #获取解禁股
    def get_classified_stock(self,year=None,month=None):
        df=ts.xsg_data(year,month)
        filename='{}-{}-classified_stock.xls'.format(year,month)
        self.save_to_excel(df,filename)

    def get_basic_info(self, retry=5):
        '''
        保存全市场数据
        :param retry:
        :return:
        '''

        engine = DBSelector().get_engine('db_stock')

        # 需要添加异常处理 重试次数
        count = 0

        while count < retry:
            try:
                df = ts.get_stock_basics()

            except Exception as e:
                self.logger.info(e)
                time.sleep(10)
                count+=1
                continue
            else:
                if df is not None:
                    df=df.reset_index()
                    df['更新日期']=datetime.datetime.now()

                    df.to_sql('tb_basic_info',engine,if_exists='replace')
                    break
                else:
                    count+=1
                    time.sleep(10)
                    continue

        if count==retry:
            self.notify(title='获取股市市场全景数据失败',desp=f'{self.__class__}')

    def save_to_excel(self,df,filename,encoding='gbk'):
        try:
            df.to_csv('temp.csv',encoding=encoding,index=False)
            df=pd.read_csv('temp.csv',encoding=encoding,dtype={'code':str})
            df.to_excel(filename,encoding=encoding)
            return True
        except Exception as e:
            self.logger.info("Save to excel faile")
            self.logger.info(e)
            return None

def main():
    obj=BasicMarket()
    obj.get_basic_info()

if __name__=='__main__':
    main()
