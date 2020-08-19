# 超时set
import datetime

class HistorySet(object):

    def __init__(self,expire=1800):
        self.data = {}
        self.expire = expire

    def add(self,value):
        now = datetime.datetime.now()
        expire = now + datetime.timedelta(seconds=self.expire)
        try: 
            hash(value) 
        except:
            raise ValueError('value not hashble')
        else:
            self.data.update({value:expire})

    def is_expire(self,value):
        # 没有过期 返回 False
        if value not in self.data or self.data[value]<datetime.datetime.now():
            return True
        else:
            return False
            