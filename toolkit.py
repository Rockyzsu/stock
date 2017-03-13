# -*-coding=utf-8-*-
#常用的工具集合
__author__ = 'Rocky'
import codecs

class Toolkit():
    @staticmethod
    def save2file( filename, content):
        # 保存为文件
        filename = filename + ".txt"
        f = open(filename, 'a')
        f.write(content)
        f.close()

    @staticmethod
    def save2filecn( filename, content):
        # 保存为文件
        filename = filename + ".txt"
        f = codecs.open(filename, 'a',encoding='utf-8')
        f.write(content)
        f.close()

    @staticmethod
    def getUserData(cfg_file):
        f=open(cfg_file,'r')
        account={}
        for i in f.readlines():
            ctype,passwd=i.split('=')
            #print ctype
            #print passwd
            account[ctype.strip()]=passwd.strip()

        return account