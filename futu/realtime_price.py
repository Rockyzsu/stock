from futu import *
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)

ret_sub, err_message = quote_ctx.subscribe(['SZ.00300'], [SubType.QUOTE], subscribe_push=False)
# 先订阅K 线类型。订阅成功后FutuOpenD将持续收到服务器的推送，False代表暂时不需要推送给脚本
if ret_sub == RET_OK:  # 订阅成功
    ret, data = quote_ctx.get_stock_quote(['SZ.00300'])  # 获取订阅股票报价的实时数据
    if ret == RET_OK:
        print(data)
        print(data['code'][0])   # 取第一条的股票代码
        print(data['code'].values.tolist())   # 转为list
    else:
        print('error:', data)
else:
    print('subscription failed', err_message)

quote_ctx.close()  # 关闭当条连接，FutuOpenD会在1分钟后自动取消相应股票相应类型的订阅