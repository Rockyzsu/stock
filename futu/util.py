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