# -*-coding=utf-8-*-

# @Time : 2018/12/20 0:25
# @File : jisilu_current.py
from datahub.jisilu import Jisilu

if __name__ == '__main__':
    obj = Jisilu(remote='qq')
    obj.daily_update()