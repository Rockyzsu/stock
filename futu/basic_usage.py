from futu import OpenQuoteContext
from collections import Iterable
def deep_print(obj):
    sep='='*20+'\n'
    print(sep)
    print(obj)
    print(sep)
    for item in dir(obj):
        if not item.startswith('__'):
            print(item,sep='\t')
    if isinstance(obj,Iterable):
        for item in obj:
            if isinstance(item,list):
                for _item in item:
                    print(_item)
            elif isinstance(item,dict):
                for k,v in item.items():
                    print(k,' : ',v)
            else:
                print(item)

quote_ctx = OpenQuoteContext(
    host='127.0.0.1',port=11111
)

data = quote_ctx.get_market_snapshot('HK.01024')
deep_print(data)
status = quote_ctx.get_global_state()
deep_print(status)



quote_ctx.close()
print('program end')


