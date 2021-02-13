import time
from futu import *
class OrderBookTest(OrderBookHandlerBase):
    def on_recv_rsp(self, rsp_pb):
        ret_code, data = super(OrderBookTest,self).on_recv_rsp(rsp_pb)
        if ret_code != RET_OK:
            print("OrderBookTest: error, msg: %s" % data)
            return RET_ERROR, data
        print("OrderBookTest ", data) # OrderBookTest自己的处理逻辑
        return RET_OK, data
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = OrderBookTest()
quote_ctx.set_handler(handler)  # 设置实时摆盘回调
quote_ctx.subscribe(['HK.00700'], [SubType.ORDER_BOOK])  # 订阅买卖摆盘类型，FutuOpenD开始持续收到服务器的推送
time.sleep(15)  #  设置脚本接收FutuOpenD的推送持续时间为15秒
quote_ctx.close()  # 关闭当条连接，FutuOpenD会在1分钟后自动取消相应股票相应类型的订阅