from futu import *
from util import deep_print
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
ret = quote_ctx.query_subscription(is_all_conn=True)
deep_print(ret)
