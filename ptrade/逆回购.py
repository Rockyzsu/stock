# 关注公众号：可转债量化分析

SH_FLAG =True
SZ_FLAG = False

def reverse_repurchase(context):
    cash = context.portfolio.cash
    #上海逆回购
    if SH_FLAG:
        amount = int((cash/100)/1000)*1000
        order('204001.SS', -amount)
    #深圳逆回购
    if SZ_FLAG:
        amount = int((cash/100)/10)*10
        order('131810.SZ', -amount)  


def initialize(context):
    '''
    初始化
    '''
    run_daily(context, reverse_repurchase, time='14:58') # 逆回购