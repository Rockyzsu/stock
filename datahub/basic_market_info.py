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
from configure.util import notify
from common.BaseService import BaseService

# 获取市场全貌

class BasicMarket(BaseService):

    def __init__(self):
        super(BasicMarket, self).__init__(f'../log/{self.__class__.__name__}.log')
        work_space=config_dict('data_path')
        self.check_path(work_space)

    def get_basic_info(self, retry=5):
        '''
        保存全市场数据
        :param retry:
        :return:
        '''
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
                break

        if count==retry:
            notify(title='获取股市市场全景数据失败',desp=f'{self.__class__.__name__}')
            exit(0)

        if df is not None:
            df = df.reset_index()
            df['更新日期'] = datetime.datetime.now()
            engine = DBSelector().get_engine('db_stock','qq')
            try:
                df.to_sql('tb_basic_info', engine, if_exists='replace',index='index',index_label='id')
            except Exception as e:
                self.logger.error(e)
                notify(title='mysql入库出错',desp=f'{self.__class__}')

def main():
    obj=BasicMarket()
    obj.get_basic_info()

if __name__=='__main__':
    main()
