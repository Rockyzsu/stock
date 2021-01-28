# -*- coding: UTF-8 -*-
"""
@author:xda
@file:etf_models.py
@time:2021/01/23
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, FLOAT,TEXT
Base = declarative_base()


class IndexObject(Base):
    __tablename__ = 'tb_etf_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    代码 = Column(String(10), unique=True)
    详细URL = Column(String(100), unique=False)
    指数名称 = Column(String(20), unique=True)
    股票数目 = Column(String(10), unique=False)
    最新收盘 = Column(FLOAT, unique=False)
    一个月收益率 = Column(FLOAT, unique=False)
    资产类别 = Column(String(20), unique=False)
    热点 = Column(String(20), unique=False)
    地区覆盖 = Column(String(20), unique=False)
    币种 = Column(String(20), unique=False)
    定制 = Column(String(20), unique=False)
    指数类别 = Column(String(20), unique=False)


class IndexObjectNew(Base):
    '''
    还用中文变量
    '''
    __tablename__ = 'etf_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    代码 = Column(String(10), unique=True)
    # 详细URL = Column(String(100), unique=False)
    指数名称 = Column(String(60), unique=False)
    指数英文名称 = Column(String(100), unique=False)
    股票数目 = Column(String(10), unique=False)
    最新收盘 = Column(FLOAT, unique=False)
    一个月收益率 = Column(FLOAT, unique=False)
    基准点数 = Column(String(20), unique=False)
    指数介绍 = Column(TEXT, unique=False)
    指数全称 = Column(String(100), unique=False)
    资产类别 = Column(String(20), unique=False)
    指数系列 = Column(String(20), unique=False)
    热点 = Column(String(20), unique=False)
    地区覆盖 = Column(String(20), unique=False)
    指数类别 = Column(String(20), unique=False)
    获取时间 =Column(DateTime)

class IndexObjectSZ(Base):
    __tablename__ = 'etf_info_sz'

    id = Column(Integer, primary_key=True, autoincrement=True)
    代码 = Column(String(20), unique=True)
    指数名称 = Column(String(100), unique=False)
    详细URL = Column(String(200), unique=False)
    基日 = Column(String(20), unique=False)
    基日指数 = Column(String(20), unique=False)
    起始计算日 = Column(String(20), unique=False)
