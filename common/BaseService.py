#-*-coding=utf-8-*-
import datetime
import os
import re
import requests
import parsel
from loguru import logger
from configure.util import notify


class BaseService(object):

    def __init__(self, logfile='default.log'):
        self.logger = logger
        self.logger.add(logfile)
        self.init_const_data()

    def init_const_data(self):
        '''
        常见的数据初始化
        '''
        self.today = datetime.datetime.now().strftime('%Y-%m-%d')


    def check_path(self, path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except Exception as e:
                self.logger.error(e)

    def get_url_filename(self, url):
        return url.split('/')[-1]


    def save_iamge(self, content, path):
        with open(path, 'wb') as fp:
            fp.write(content)

    def get(self, _josn=False, binary=False, retry=5):

        start = 0
        while start < retry:

            try:
                r = requests.get(
                    url=self.url,
                    params=self.params,
                    headers=self.headers,
                    cookies=self.cookie)

            except Exception as e:
                start += 1
                continue

            else:
                if _josn:
                    result = r.json()
                elif binary:
                    result = r.content
                else:
                    result = r.text
                return result

        return None

    def post(self, post_data, _josn=False, binary=False, retry=5):

        start = 0
        while start < retry:

            try:
                r = requests.post(
                    url=self.url,
                    headers=self.headers,
                    data=post_data
                )

            except Exception as e:
                start += 1
                continue

            else:
                if _josn:
                    result = r.json()
                elif binary:
                    result = r.content
                else:
                    result = r.text
                return result

        return None

    def parse(self, content):
        '''
        页面解析
        '''
        response = parsel.Selector(text=content)

        return None

    def process(self, data, history=False):
        '''
        数据存储
        '''
        pass

    def trading_time(self):
        '''
        判定时候交易时间 0 为交易时间， 1和-1为非交易时间
        :return:
        '''
        TRADING = 0
        MORNING_STOP = -1
        AFTERNOON_STOP = 1

        current = datetime.datetime.now()
        year, month, day = current.year, current.month, current.day
        start = datetime.datetime(year, month, day, 9, 23, 0)
        noon_start = datetime.datetime(year, month, day, 12, 58, 0)

        morning_end = datetime.datetime(year, month, day, 11, 31, 0)
        end = datetime.datetime(year, month, day, 15, 2, 5)

        if current > start and current < morning_end:
            return TRADING

        elif current > noon_start and current < end:
            return TRADING

        elif current > end:
            return AFTERNOON_STOP

        elif current < start:
            return MORNING_STOP

    def notify(self,title='',desp=''):
        notify(title,desp)

    def weekday(self,day=datetime.datetime.now().strftime('%Y-%m-%d')):
        '''判断星期几'''

        if re.search('\d{4}-\d{2}-\d{2}',day):
            fmt = '%Y-%m-%d'
        elif re.search('\d{8}',day):
            fmt = '%Y%m%d'
        else:
            raise ValueError('请输入正确的日期格式')

        current_date = datetime.datetime.strptime(day,fmt)
        year_2000th =datetime.datetime(year=2000,month=1,day=2)
        day_diff = current_date-year_2000th
        return day_diff.days%7

    def is_weekday(self,day=datetime.datetime.now().strftime('%Y-%m-%d')):
        if self.weekday(day) in [0,6]:
            return False
        else:
            return True

    def execute(self, cmd, data, conn):

        cursor = conn.cursor()

        if not isinstance(data, tuple):
            data = (data,)
        try:
            cursor.execute(cmd, data)
        except Exception as e:
            conn.rollback()
            print('执行数据库错误 {}'.format(e))
            ret = None
        else:
            ret = cursor.fetchall()
            conn.commit()

        return ret


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


if __name__ == '__main__':
    base = BaseService()
    base.is_weekday()




