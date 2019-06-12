#-*-coding=utf-8-*-
# 每天收盘收运行
import datetime
import time

__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
import tushare as ts
import os
from setting import get_engine,llogger,is_holiday,DATA_PATH
import pandas as pd
filename=os.path.basename(__file__)
logger = llogger('log/'+filename)

class SaveData():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    daily_engine = get_engine('db_daily')

    def __init__(self):
        work_space=DATA_PATH
        if os.path.exists(work_space) ==False:
            os.mkdir(work_space)
        os.chdir(work_space)


    @staticmethod
    def daily_market():
        df = ts.get_today_all()
        try:
            df.to_sql(SaveData.today,SaveData.daily_engine,if_exists='replace')
        except Exception as e:
            logger.info(e)
        logger.info("Save {} data to MySQL".format(SaveData.today))

    #获取解禁股
    def get_classified_stock(self,year=None,month=None):
        df=ts.xsg_data(year,month)
        filename='{}-{}-classified_stock.xls'.format(year,month)
        self.save_to_excel(df,filename)

    def basic_info(self,retry=5):
        engine = get_engine('db_stock')

        # 需要添加异常处理 重试次数
        count = 0

        while count < retry:
            try:
                df = ts.get_stock_basics()

            except Exception as e:
                logger.info(e)
                time.sleep(10)
                count+=1
                continue
            else:
                if df is not None:
                    df=df.reset_index()
                    df['更新日期']=datetime.datetime.now()

                    df.to_sql('tb_basic_info',engine,if_exists='replace')
                    logger.info('入库成功')
                    break
                else:
                    count+=1
                    time.sleep(10)
                    continue



    def save_to_excel(self,df,filename,encoding='gbk'):
        try:
            df.to_csv('temp.csv',encoding=encoding,index=False)
            df=pd.read_csv('temp.csv',encoding=encoding,dtype={'code':str})
            df.to_excel(filename,encoding=encoding)
            return True
        except Exception as e:
            logger.info("Save to excel faile")
            logger.info(e)
            return None

def main():
    obj=SaveData()
    obj.basic_info()

if __name__=='__main__':

    main()
    logger.info('完成')