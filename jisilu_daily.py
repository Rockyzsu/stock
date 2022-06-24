# -*-coding=utf-8-*-

# @Time : 2018/12/20 0:25
# @File : jisilu_current.py
from datahub.jisilu import Jisilu
import fire

def run(remote='qq'):
    obj = Jisilu(remote=remote)
    obj.daily_update()

if __name__ == '__main__':
    fire.Fire(run)

# shell :
# python jisilu.py --remote=qq