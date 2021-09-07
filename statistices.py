#-*-coding=utf-8-*-
'''
用于统计数据
'''
import alert
'''
计算收益
sold 卖价
buy 买入价
'''
def percentage(sold,buy):
    x=(sold-buy)*1.00/buy*100
    print(round(x,2))
    return x

'''
计算买入价
sold: 卖出的价格
需要的幅度
'''
def plan_buy_price(sold,percent):
    buy=sold*1.00/(1+percent*1.00/100)
    print(round(buy,2))
    return buy

#percentage(0.196,0.188)
# plan_buy_price(10,10)

a=1.567
print(round(a,2))
