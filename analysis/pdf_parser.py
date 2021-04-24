# -*- coding: utf-8 -*-
# @Time : 2021/4/21 22:27
# @File : pdf_parser.py
# @Author : Rocky C@www.30daydo.com
import datetime
import os
from pathlib import PurePath
import glob
today = datetime.datetime.now().strftime('%Y-%m-%d')
BASE=PurePath(__file__).parent.parent
root = PurePath.joinpath(BASE,'fund',today,'*.pdf')
# print(root)

PDF_PATH = None

class PDFParserCls():
    def __init__(self):
        pass

    def walk_pdf(self):
        for file in glob.glob(str(root)):
            print(file)

    def parse(self,pdf_file):


def main():
    app = PDFParserCls()
    app.walk_pdf()


if __name__ == '__main__':
    main()
