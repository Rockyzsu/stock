#-*-coding=utf-8-*-
'''
用于统计数据
'''
import alert
def percentage(sold,buy):
    d=(sold-buy)*1.00/buy*100
    print round(d,2)


percentage(0.014,0.0089)