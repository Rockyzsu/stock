# -*-coding=utf-8-*-

# @Time : 2018/12/20 0:25
# @File : jisilu_current.py
from jisilu import Jisilu

if __name__ == '__main__':
    obj = Jisilu(check_holiday=True)
    obj.daily_update()