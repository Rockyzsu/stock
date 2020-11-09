#-*-coding=utf-8-*-
import os
from loguru import logger
import requests
import config

class BaseService:

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

    def notify(self,text):
            url = f"https://sc.ftqq.com/{config.WECHAT_ID}.send?text=" + text
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

