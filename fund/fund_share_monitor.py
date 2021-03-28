# -*- coding: UTF-8 -*-
"""
@author:xda
@file:fund_share_monitor.py
@time:2021/01/27
"""
# 份额监控,对上一天额度出现较大申购进行监控

import sys
sys.path.append('..')
from configure.settings import DBSelector
from common.BaseService import BaseService
from fund.fund_share_crawl import ShareModel,FundBaseInfoModel,Fund
from sqlalchemy import and_
class ShareMonitor(Fund):

    def __init__(self,):
        super(ShareMonitor, self).__init__()

        self.sess = self.get_session()()


    def query(self,code,date):
        # last_date =
        obj = self.sess.query(ShareModel).filter(and_(ShareModel.date<=date, ShareModel.code==code)).all()
        # print(obj)
        if obj:
            for i in obj:
                print(i.code)
                print(i.share)
                print(i.date)
                print('')


if __name__ == '__main__':
    app = ShareMonitor()
    code = '167302'
    date = '2021-01-26'
    app.query(code=code,date=date)
