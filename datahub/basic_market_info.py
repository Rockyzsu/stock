__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''

import datetime
import time
import tushare as ts
import sys
sys.path.append('..')
from configure.settings import DBSelector,config_dict
from common.BaseService import BaseService

# 获取市场全貌

class BasicMarket(BaseService):

    def __init__(self):
        super(BasicMarket, self).__init__(f'../log/{self.__class__.__name__}.log')
        work_space=config_dict('data_path')
        ts_token=config_dict('ts_token')
        self.check_path(work_space)
        ts.set_token(ts_token)
        self.pro = ts.pro_api()

    def get_basic_info(self, retry=5):
        '''
        保存全市场数据
        :param retry:
        :return:
        '''
        # 需要添加异常处理 重试次数
        count = 0
        df = None
        while count < retry:
            try:
                df = self.pro.stock_basic(exchange='', list_status='', fields='')
            except Exception as e:
                self.logger.info(e)
                time.sleep(10)
                count+=1
                continue
            else:
                break

        if count==retry:
            self.notify(title=f'{self.__class__.__name__}获取股市市场全景数据失败')
            exit(0)

        if df is not None:
            df = df.reset_index(drop=True)
            df.rename(columns={'symbol':'code'},inplace=True)
            df['更新日期'] = datetime.datetime.now()
            engine = DBSelector().get_engine('db_stock','qq')
            try:
                df.to_sql('tb_basic_info', engine, if_exists='replace')
            except Exception as e:
                self.logger.error(e)
                self.notify(title=f'{self.__class__}mysql入库出错')

        return df

def main():
    obj=BasicMarket()
    obj.get_basic_info()

if __name__=='__main__':
    main()
