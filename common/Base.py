# -*- coding: utf-8 -*-
# @Time : 2021/4/2 20:02
# @File : Base.py
# @Author : Rocky C@www.30daydo.com


import xcsc_tushare as xc
import sys
sys.path.append('..')
from configure.settings import config
xc_token_pro=config.get('xc_token_pro')
xc.set_token(xc_token_pro)
simulation_server = config.get('xc_server')
pro =xc.pro_api(env='prd',server=simulation_server)
__all__=('pro',)
