# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
import sys
sys.path.append('..')
import re
import time
import datetime
import requests
import pandas as pd
from configure.settings import DBSelector, send_from_aliyun
from sqlalchemy import VARCHAR
from common.BaseService import BaseService


# 爬取集思录 可转债的数据
class Jisilu(BaseService):
    def __init__(self, check_holiday=False, remote='qq'):
        super(Jisilu, self).__init__(logfile='log/jisilu.log')

        if check_holiday:
            self.check_holiday()

        self.date = datetime.datetime.now().strftime('%Y-%m-%d')
        # self.date = '2020-02-07' # 用于调整时间

        self.timestamp = int(time.time() * 1000)
        self.headers = {
            'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'}
        self.url = 'https://www.jisilu.cn/data/cbnew/cb_list/?___jsl=LST___t={}'.format(self.timestamp)
        self.pre_release_url = 'https://www.jisilu.cn/data/cbnew/pre_list/?___jsl=LST___t={}'.format(self.timestamp)
        self.remote = remote
        self.DB = DBSelector()
        self.engine = self.DB.get_engine('db_jisilu', self.remote)

    def check_holiday(self):
        if self.is_weekday():
            self.logger.info("Start")
        else:
            self.logger.info("Holidy")
            exit(0)

    def download(self, url, data, retry=5):

        for i in range(retry):
            try:
                r = requests.post(url, headers=self.headers, data=data)
                if not r.text or r.status_code != 200:
                    continue
                else:
                    return r
            except Exception as e:
                self.logger.info(e)
                self.notify(title='下载失败', desp=f'{self.__class__}')
                continue

        return None

    def daily_update(self, adjust_no_use=True):

        post_data = {
            'btype': 'C',
            'listed': 'Y',
            'rp': '50',
            'is_search': 'N',
        }

        js = self.download(self.url, data=post_data)
        if not js:
            return None

        ret = js.json()
        bond_list = ret.get('rows', {})
        self.data_parse(bond_list, adjust_no_use)

    def data_parse(self, bond_list, adjust_no_use):

        cell_list = []
        for item in bond_list:
            cell_list.append(pd.Series(item.get('cell')))
        df = pd.DataFrame(cell_list)

        if adjust_no_use:

            # 类型转换 部分含有%
            df['premium_rt'] = df['premium_rt'].map(lambda x: float(x.replace('%', '')))
            df['price'] = df['price'].astype('float64')
            df['convert_price'] = df['convert_price'].astype('float64')
            df['premium_rt'] = df['premium_rt'].astype('float64')
            df['redeem_price'] = df['redeem_price'].astype('float64')

            def convert_float(x):
                try:
                    ret_float = float(x)
                except:
                    ret_float = None
                return ret_float

            def convert_percent(x):
                try:
                    ret = float(x) * 100
                except:
                    ret = None
                return ret

            def remove_percent(x):
                try:
                    ret = x.replace(r'%', '')
                    ret = float(ret)
                except Exception as e:
                    ret = None

                return ret

            df['put_convert_price'] = df['put_convert_price'].map(convert_float)
            df['sprice'] = df['sprice'].map(convert_float)
            df['ration'] = df['ration'].map(convert_percent)
            df['volume'] = df['volume'].map(convert_float)
            df['convert_amt_ratio'] = df['convert_amt_ratio'].map(remove_percent)
            df['ration_rt'] = df['ration_rt'].map(convert_float)
            df['increase_rt'] = df['increase_rt'].map(remove_percent)
            df['sincrease_rt'] = df['sincrease_rt'].map(remove_percent)

            rename_columns = {'bond_id': '可转债代码', 'bond_nm': '可转债名称', 'price': '可转债价格', 'stock_nm': '正股名称',
                              'stock_cd': '正股代码',
                              'sprice': '正股现价',
                              'sincrease_rt': '正股涨跌幅',
                              'convert_price': '最新转股价', 'premium_rt': '溢价率', 'increase_rt': '可转债涨幅',
                              'put_convert_price': '回售触发价', 'convert_dt': '转股起始日',
                              'short_maturity_dt': '到期时间', 'volume': '成交额(万元)',
                              'redeem_price': '强赎价格', 'year_left': '剩余时间',
                              'next_put_dt': '回售起始日', 'rating_cd': '评级',
                              # 'issue_dt': '发行时间',
                              # 'redeem_tc': '强制赎回条款',
                              # 'adjust_tc': '下修条件',
                              'adjust_tip': '下修提示',
                              # 'put_tc': '回售',
                              'adj_cnt': '下调次数',
                              #   'ration':'已转股比例'
                              'convert_amt_ratio': '转债剩余占总市值比',
                              'curr_iss_amt': '剩余规模', 'orig_iss_amt': '发行规模',
                              'ration_rt': '股东配售率',
                              'redeem_flag': '发出强赎公告',
                              'redeem_dt': '强赎日期',
                              }

            df = df.rename(columns=rename_columns)
            df = df[list(rename_columns.values())]
            df['更新日期'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        df = df.set_index('可转债代码', drop=True)

        try:

            df.to_sql('tb_jsl_{}'.format(self.date), self.engine, if_exists='replace', dtype={'可转债代码': VARCHAR(10)})
            db_stock = self.DB.get_engine('db_stock', self.remote)
            df.to_sql('tb_bond_jisilu'.format(self.date), db_stock, if_exists='replace', dtype={'可转债代码': VARCHAR(10)})

        except Exception as e:
            self.logger.info(e)
            send_from_aliyun(title='jisilu可转债', content='写入数据库出错')

    def init_release_table(self, conn):

        creat_table = '''
        create table if not exists tb_bond_release (
        可转债代码 varchar(10),
        可转债名称 varchar(10),
        集思录建议 varchar(500),
        包销比例 float(6,3),
        中签率 float(6,3),
        上市日期 varchar(20),
        申购户数（万户） int,
        单账户中签（顶格） float(6,3),
        股东配售率 float(6,3),
        评级 varchar(8),
        现价比转股价 float(6,3),
        抓取时间 datetime
        );
        '''
        self.execute(creat_table,(),conn)


    def get_conn(self):
        return self.DB.get_mysql_conn('db_stock','qq')

    # 这个数据最好晚上10点执行
    def release_data(self):

        conn = self.get_conn()
        self.init_release_table(conn)
        post_data = {'cb_type_Y': 'Y',
                     'progress': '',
                     'rp': 22,
                     }

        r = self.download(url=self.pre_release_url, data=post_data)
        js_data = r.json()
        rows = js_data.get('rows')
        self.save_release_data(rows, conn)

    def save_release_data(self, rows, conn):
        for items in rows:
            item = items.get('cell')
            single_draw = item.get('single_draw')
            if single_draw:
                jsl_advise_text = item.get('jsl_advise_text')  # 集思录建议
                underwriter_rt = self.convert_float(item.get('underwriter_rt'))  # 包销比例
                bond_nm = item.get('bond_nm')
                lucky_draw_rt = self.convert_float(item.get('lucky_draw_rt'))  # 中签率
                if lucky_draw_rt:
                    lucky_draw_rt = lucky_draw_rt * 100
                list_date = item.get('list_date')
                valid_apply = self.convert_float(item.get('valid_apply'))  # 申购户数（万户）
                single_draw = self.convert_float(item.get('single_draw'))  # 单账户中签（顶格）
                ration_rt = self.convert_float(item.get('ration_rt'))  # 股东配售率
                rating_cd = item.get('rating_cd')  # 评级
                bond_id = item.get('bond_id')  # 可转债代码
                pma_rt = self.convert_float(item.get('pma_rt'))  # 现价比转股价
                update_time = datetime.datetime.now()

                if self.check_bond_exist(bond_id, conn):
                    if self.check_update(bond_id, conn):
                        update_data = (underwriter_rt, list_date, update_time, bond_id)
                        self.update_release_data(update_data, conn)
                    else:
                        continue

                # 插入
                else:
                    insert_data_tuple = (
                        bond_id, bond_nm, jsl_advise_text, underwriter_rt, lucky_draw_rt, list_date, valid_apply,
                        single_draw, ration_rt, rating_cd, pma_rt, update_time)
                    self.insert_release_data(insert_data_tuple, conn)

    def check_update(self, bond_id, conn):
        check_update = '''select * from tb_bond_release where 可转债代码=%s and 包销比例 is null'''
        return self.execute(check_update, bond_id, conn)

    def update_release_data(self, update_data, conn):
        '''更新发布数据'''

        update_sql = '''update tb_bond_release set 包销比例=%s , 上市日期=%s ,抓取时间=%s where 可转债代码 = %s'''
        self.execute(update_sql, update_data, conn)

    def insert_release_data(self, data, conn):
        '''插入发布数据'''
        insert_sql = '''insert into tb_bond_release (可转债代码 , 可转债名称 , 集思录建议 , 包销比例 , 中签率 ,上市日期 ,申购户数（万户）, 单账户中签（顶格）, 股东配售率 ,评级 ,  现价比转股价,抓取时间) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        self.execute(insert_sql, data, conn)

    def check_bond_exist(self, bond_id, conn):
        '''
        判断债券是否存在
        '''
        check_exist = '''select * from tb_bond_release where 可转债代码=%s'''
        return self.execute(check_exist, bond_id, conn)

    def execute(self, cmd, data, conn):
        cursor = conn.cursor()
        if not isinstance(data, tuple):
            data = (data,)
        try:
            cursor.execute(cmd, data)
        except Exception as e:
            conn.rollback()
            self.logger.error('执行数据库错误 {}'.format(e))
            ret = None
        else:
            ret = cursor.fetchall()
            conn.commit()

        return ret

    def convert_float(self, x):
        if not x:
            return None

        if '%' in x:
            ration = 100
        else:
            ration = 1

        x = re.sub('%', '', x)
        try:
            ret = float(x) * ration
        except Exception as e:
            self.logger.error('转换失败{}'.format(e))
            ret = None

        return ret


def main():
    obj = Jisilu(check_holiday=False)
    # obj.daily_update()
    obj.release_data()


if __name__ == '__main__':
    main()
