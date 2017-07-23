#-*-coding=utf-8-*-
'''
用于统计数据
'''
import alert
def percentage(sold,buy):
    x=(sold-buy)*1.00/buy*100
    print round(x,2)
    return x

def buy_price(sold,percent):
    buy=sold*1.00/(1+percent*1.00/100)
    print round(buy,2)
    return buy

#percentage(0.196,0.188)
buy_price(0.196,10)

