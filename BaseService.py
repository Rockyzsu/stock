#-*-coding=utf-8-*-
import os
from loguru import logger
import requests
import config

class BaseService(object):

    def __init__(self, logfile='default.log'):
        self.logger = logger
        self.logger.add(logfile)

    def check_path(self, path):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except Exception as e:
                self.logger.error(e)

    def get_filename(self, url):
        return url.split('/')[-1]

    def notify(self,title='',desp=''):
            url = f"https://sc.ftqq.com/{config.WECHAT_ID}.send?text={title}&desp={desp}"
            try:
                res = requests.get(url)
            except Exception as e:
                print(e)
                return False
            else:
                return True

    def save_iamge(self, content, path):
        with open(path, 'wb') as fp:
            fp.write(content)

    def get(self,url):
        raise NotImplemented

    def post(self):
        raise NotImplemented

if __name__ == '__main__':
    obj = BaseService()
    obj.notify(title='hello', desp='world')
