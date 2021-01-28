# -*- coding: UTF-8 -*-
"""
@author:xda
@file:util.py
@time:2021/01/24
"""
import json

def jsonp2json(str_):
    return json.loads(str_[str_.find('{'):str_.rfind('}')+1])


if __name__ == '__main__':
    pass
