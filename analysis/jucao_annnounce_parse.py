# -*- coding: utf-8 -*-
# @Time : 2021/4/21 19:01
# @File : jucao_annnounce_parse.py
# @Author : Rocky C@www.30daydo.com
import datetime
import os
import sys
import time

sys.path.append('..')
from common.BaseService import BaseService
from configure.settings import DBSelector
from threading import Thread
from queue import Queue
from pathlib import PurePath
BASE = PurePath(__file__).parent

class PDFParseproducer(Thread):

    def __init__(self, q,date=None):
        super(PDFParseproducer, self).__init__()
        if date is None:
            self.date = datetime.datetime.now().strftime('%Y-%m-%d')
        else:
            self.date=date
        self.doc = DBSelector().mongo('qq')['db_stock']['jucao_announcement']
        self.q = q
        print('Producer start')

    def gen_date_list(self):
        current = datetime.datetime.now() + datetime.timedelta(days=1)
        last_day_count = 20
        date_list=[]
        for i in range(last_day_count):
            slide_day = (current+datetime.timedelta(days=-1*i)).strftime('%Y-%m-%d')
            date_list.append(slide_day)
        return date_list

    def run(self):
        for d in self.gen_date_list():
            print(d)
            # pending_data = self.doc.find({'analysis': {'$exists': False},'announcementTime':self.date})
            pending_data = self.doc.find({'analysis': {'$exists': False},'announcementTime':d})
            pending_data_list = list(pending_data)

            if len(pending_data_list) == 0:
                # 数据已为空了
                continue

            for item in pending_data_list:
                code=item['code']
                code_list=code.split(',')
                if any(map(lambda x:x.startswith(('16','501','502')),code_list)):

                    task_data = {
                        'url': item['url'],
                        'announcementId': item['announcementId'],
                        'title': item['title'],
                        'secName': item['secName'],
                        'date':item['announcementTime'],
                        'code':code[:6],
                    }
                    print('pushing data',code,item['secName'])
                    self.q.put(task_data)


class JuCaoParser(BaseService, Thread):

    def __init__(self, q):
        BaseService.__init__(self, '../log/jucao_parser.log')
        Thread.__init__(self)
        self.q = q

        self.params = None
        self.db = DBSelector().mongo('qq')
        self.doc = self.db['db_stock']['jucao_announcement']
        print('download thread start!')

    def run(self):
        print('running....... in thread')

        while not self.q.empty():
            data = self.q.get()
            # print(data)
            url = data['url']
            secName = data['secName']
            title = data['title']
            announcementId = data['announcementId']
            date=data['date']
            code=data['code']
            PARENT_FOLDER=os.path.join(BASE,date)
            self.check_path(PARENT_FOLDER)

            try:
                content = self.get(
                    url=url,
                    _json=False,
                    binary=True
                )

            except Exception as e:
                self.logger.error(e)
            else:
                filename = f'{code}_{announcementId}_{secName[:50]}_{title[:50]}.pdf'
                full_path = os.path.join(PARENT_FOLDER, filename)
                with open(full_path, 'wb') as fp:
                    fp.write(content)

                self.doc.update_one({'announcementId': announcementId}, {'$set': {'analysis': True}})

    @property
    def headers(self):
        return {
            'Referer': 'http://www.cninfo.com.cn/new/commonUrl/pageOfSearch?url=disclosure/list/search&lastPage=index',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'
        }


def main():
    q = Queue()
    producer = PDFParseproducer(q)
    producer.start()
    time.sleep(5)
    thread_num = 4
    thread_list=[]

    for i in range(thread_num):
        app = JuCaoParser(q)
        thread_list.append(app)

    for t in thread_list:
        t.start()

    for t in thread_list:
        t.join()

if __name__ == '__main__':
    main()
