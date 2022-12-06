# 集思录可转债公告数据
import datetime
import time
import pandas as pd
import requests
from jsl_login import main as get_bond_info

# 下修
class Announcement:

    def __init__(self, kw):
        self.url = 'https://www.jisilu.cn/data/cbnew/announcement_list/?___jsl=LST___t={}'
        self.headers = {'Accept': 'application/json, text/javascript, */*; q=0.01',

                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'Host': 'www.jisilu.cn',
                        'Origin': 'https://www.jisilu.cn',
                        'Referer': 'https://www.jisilu.cn/data/cbnew/announcement/',
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
                        'X-Requested-With': 'XMLHttpRequest',
                        }
        self.kw = kw
        today = datetime.datetime.now().strftime('%Y%m%d')

        self.path = '../data/{}-{}.xlsx'.format(self.kw, today)

    def bond_info(self):
        code_list = get_bond_info()['bond_id'].tolist()
        return code_list

    def crawl(self, code):
        ts = int(time.time())
        data = {'code': code,
                'title': self.kw,
                'tp[]': 'Y',
                'rp': '22'}
        req = requests.post(
            url=self.url.format(ts),
            headers=self.headers,
            data=data
        )
        return req.json()

    def parse(self, content):
        latest_date = None
        latest_news = None
        for row in content['rows']:
            cell = row['cell']
            anno_tm = cell['anno_tm']
            if latest_date is None or latest_date < anno_tm:
                latest_date = anno_tm
                latest_news = cell
                print(cell)

        return latest_news

    def run(self):
        result = []
        for code in self.bond_info():
            content = self.crawl(code)
            cell = self.parse(content)
            if cell is None:
                continue

            result.append(cell)
        df = pd.DataFrame(result)
        df = df.rename(
            columns={'bond_id': '代码', 'anno_dt': '公告日期', 'stock_nm': '正股名称', 'stock_id': '正股代码',
                     'anno_url': '公告url', 'anno_title': '公告标题'})
        df.to_excel(self.path, encoding='utf8')

    def persistence(self):
        # 读取整理的excel文件到mongodb
        # import numpy as np
        df = pd.read_excel(self.path, index_col=None, dtype={'正股代码': str, '代码': str})
        import sys
        sys.path.append('..')
        from configure.settings import DBSelector
        client = DBSelector().mongo('qq')
        doc = client['db_parker']['Not_LowDown_ConvertPrice']
        for index, row in df.iterrows():
            code = row['代码']
            announce_date = row['公告日期']
            if not doc.find_one({'代码': code, '公告日期': announce_date}):
                try:
                    re_calculate_date = row['重新计算日期']
                except:
                    re_calculate_date = None
                # 修改过得excel
                # doc.insert_one({'代码':row['代码'],'重新计算日期':re_calculate_date,'公告日期':row['公告日期'],'正股代码':row['正股代码'],'正股名称':row['正股名称'],'公告标题':row['公告标题']})

                doc.insert_one({'代码': row['代码'], '重新计算日期': re_calculate_date, '公告日期': row['公告日期'],
                                '正股代码': row['正股代码'], '正股名称': row['正股名称'], '公告标题': row['公告标题'],'公告链接':row['公告url']})
                # doc.update_one({'代码': code, '公告日期': announce_date},{'$set':{'公告链接':row['公告标题']}})

                print('update one {}'.format(row['代码']))

    def update_only(self):
        # 临时更新数据
        import os
        import sys
        sys.path.append('..')
        from configure.settings import DBSelector
        client = DBSelector().mongo('qq')
        doc = client['db_parker']['Not_LowDown_ConvertPrice']
        path_list = [
            # '不向下修-20220824.xlsx',
                     '不向下修-20220925.xlsx',
            # '不向下修-20221025.xlsx'
        ]
        for path in path_list:
            df = pd.read_excel(os.path.join('../data',path), index_col=None, dtype={'正股代码': str, '代码': str})
            for index, row in df.iterrows():
                code = row['代码']
                announce_date = row['公告日期']
                if not doc.find_one({'代码': code, '公告日期': announce_date}):
                    try:
                        re_calculate_date = row['重新计算日期']
                    except:
                        re_calculate_date = None
                    doc.insert_one({
                        '代码': row['代码'],
                        '转债名称': row['转债名称'],
                        '重新计算日期': re_calculate_date,
                        '公告日期': row['公告日期'],
                        '正股代码': row['正股代码'],
                        '正股名称': row['正股名称'],
                        '公告标题': row['标题'], '公告链接': row['公告url']})

                # print(item)
                # title = item['公告标题']
                # if title.startswith('http'):
                # doc.update_one({'_id':item['_id']},{'$set':{'公告链接':title}})


def main():
    # 不向下修 可能满足赎回 不提前赎回
    kw = '不向下修'
    app = Announcement(kw)
    app.run()  # 下载到本地
    app.persistence()  # 持久化到mongodb
    # app.update_only()


if __name__ == '__main__':
    main()
