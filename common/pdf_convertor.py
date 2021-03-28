# -*- coding: utf-8 -*-
# @Time : 2021/3/19 1:01
# @File : pdf_convertor.py
# @Author : Rocky C@www.30daydo.com


import pdfplumber
path=r'D:\Photo\s素材\da83e97d-29aa-49ea-9783-e25abe402012.pdf'
def pdf_convert_txt(filename):
    with pdfplumber.open(filename) as pdf:
        content = ''
        #len(pdf.pages)为PDF文档页数
        for i in range(len(pdf.pages)):
            #pdf.pages[i] 是读取PDF文档第i+1页
            page = pdf.pages[i]
            #page.extract_text()函数即读取文本内容，下面这步是去掉文档最下面的页码
            page_content = '\n'.join(page.extract_text().split('\n')[:-1])
            content = content + page_content
        print(content)
        return content
