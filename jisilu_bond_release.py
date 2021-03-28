# -*-coding=utf-8-*-

# @Time : 2018/12/20 0:20
# @File : jisilu_call.py
from datahub.jisilu import Jisilu


def main():
    obj = Jisilu(remote='qq')
    obj.release_data()


if __name__ == '__main__':
    main()
