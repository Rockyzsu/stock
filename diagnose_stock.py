# -*-coding=utf-8-*-

__author__ = 'Rocky'
'''
http://30daydo.com
Email: weigesysu@qq.com
'''
import re
from configure.settings import get_mysql_conn
# 是否黑名单
def check_blacklist(code):
    conn = get_mysql_conn('db_stock')
    cur = conn.cursor()
    cmd = 'select * from tb_blacklist where code=\'{}\''.format(code)
    cur.execute(cmd)
    ret = cur.fetchone()
    if len(ret)==0:
        return False
    else:
        print(ret[3])
        return True
# 是否是东北的
def dongbei(code):
    dongbei_area = ['黑龙江','吉林','辽宁']
    conn = get_mysql_conn('db_stock')
    cur = conn.cursor()
    cmd = 'select area from tb_basic_info where code=\'{}\''.format(code)
    cur.execute(cmd)
    ret = cur.fetchone()
    if ret[0] in dongbei_area:
        return True
    else:
        return False

def get_code(name):
    conn = get_mysql_conn('db_stock')
    cur = conn.cursor()
    cmd = 'select code from tb_basic_info where name=\'{}\''.format(name)
    cur.execute(cmd)
    ret = cur.fetchone()
    return ret[0]

def diagnose(code):
    if check_blacklist(code):
        print('存在黑名单')

    if dongbei(code):
        print('东北股')



def main():
    ipt = raw_input('输入诊断个股的代码或者名称: ')
    if not re.search('\d{6}',ipt):
        code = get_code(ipt)

    print(code)
    diagnose(code)


if __name__ == '__main__':
    main()