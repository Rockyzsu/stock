# -*- coding: utf-8 -*-
# @Time : 2021/3/29 22:30
# @File : LOF_Model.py
# @Author : Rocky C@www.30daydo.com
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, INTEGER, VARCHAR, DATE, DateTime, ForeignKey, FLOAT

# 创建对象的基类:
Base = declarative_base()


class FundBaseInfoModel(Base):
    # 基本表
    # 表的名字:
    __tablename__ = 'LOF_BaseInfo'

    # 表的结构:
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    code = Column(VARCHAR(6), comment='基金代码', unique=True)
    name = Column(VARCHAR(40), comment='基金名称')
    category = Column(VARCHAR(8), comment='基金类别')
    invest_type = Column(VARCHAR(6), comment='投资类别')
    manager_name = Column(VARCHAR(48), comment='管理人呢名称')
    issue_date = Column(DATE, comment='上市日期')
    # child = relationship('ShareModel', back_populates='LOF_BaseInfo')
    child = relationship('ShareModel')

    def __str__(self):
        return f'<{self.code}><{self.name}>'


class ShareModel(Base):
    # 详情表 不只是LOF，ETF，封基也被包含了
    # 表的名字:
    __tablename__ = 'LOF_Share'

    # 表的结构:

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    code = Column(VARCHAR(6), ForeignKey('LOF_BaseInfo.code'), comment='代码')
    date = Column(DATE, comment='份额日期')
    share = Column(FLOAT, comment='份额 单位：万份')
    parent = relationship('FundBaseInfoModel')
    # parent = relationship('FundBaseInfoModel', back_populates='LOF_Share')
    crawltime = Column(DateTime, comment='爬取日期')

