#-*-coding=utf-8-*-
__author__ = 'xda'
def getUserData():
    f=open("data.cfg",'r')
    account={}
    for i in f.readlines():
        ctype,passwd=i.split('=')
        #print ctype
        #print passwd
        account[ctype.strip()]=passwd.strip()

    return account

if __name__=="__main__":
    data=getUserData()
    print data