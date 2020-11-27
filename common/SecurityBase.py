# -*- coding: utf-8 -*-
# @Time : 2020/11/26 15:14
# @File : SecurityBase.py
# @Author : Rocky C@www.30daydo.com

import re

class StockBase:

    def __init__(self):
        pass

    def valid_code(self,code):
        pattern =  re.search('(\d{6})', code)
        if pattern:
            code = pattern.group(1)
        else:
            code = None

        return code
