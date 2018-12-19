# -*-coding=utf-8-*-
import time
import datetime
import requests
import pandas as pd
from setting import get_engine, llogger, is_holiday
import six
from send_mail import sender_21cn
from sqlalchemy import VARCHAR

engine = get_engine('db_stock')
logger = llogger(__file__)


# 爬取集思录 可转债的数据
class Jisilu:
    def __init__(self):
        # py2
        if six.PY2:
            self.timestamp = long(time.time() * 1000)
        else:
            self.timestamp = int(time.time() * 1000)
        self.headers = {
            'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'}

        self.post_data = {
            'btype': 'C',
            'listed': 'Y',
            'rp': '50',
            'is_search':'N',
        }
        self.url = 'https://www.jisilu.cn/data/cbnew/cb_list/?___jsl=LST___t={}'.format(self.timestamp)

    def download(self, url, retry=5):
        for i in range(retry):
            try:
                r = requests.post(url, headers=self.headers, data=self.post_data)
                if not r.text or r.status_code != 200:
                    continue
                else:
                    return r
            except Exception as e:
                logger.info(e)
                sender_21cn('jisilu可转债', '异常信息>>>>{}'.format(e))
                continue
        return None

    def dataframe(self, adjust_no_use=True):
        js = self.download(self.url)
        if not js:
            return None
        ret = js.json()
        bond_list = ret.get('rows')
        cell_list = []
        for item in bond_list:
            cell_list.append(pd.Series(item.get('cell')))
        df = pd.DataFrame(cell_list)

        # 下面的数据暂时不需要
        if adjust_no_use:
            # del df['active_fl']
            # del df['adq_rating']
            # del df['list_dt']
            # del df['left_put_year']
            # del df['owned']
            # del df['put_dt']
            # del df['real_force_redeem_price']
            # del df['redeem_dt']
            # del df['apply_cd']
            # del df['force_redeem']
            # del df['stock_id']
            # del df['full_price']
            # del df['pre_bond_id']
            # del df['ytm_rt']
            # del df['ytm_rt_tax']
            # del df['repo_cd']
            # del df['last_time']
            # del df['pinyin']
            # del df['put_real_days']
            # del df['price_tips']
            # del df['btype']
            # del df['repo_valid']
            # del df['repo_valid_to']
            # del df['repo_valid_from']
            # del df['repo_discount_rt']
            # del df['adjust_tc']
            # del df['cpn_desc']
            # del df['market']
            # del df['stock_net_value']

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
                    ret = float(x)*100
                except:
                    ret = None
                return ret

            def remove_percent(x):
                try:
                    ret = x.replace(r'%','')
                    ret = float(ret)
                except Exception as e:
                    ret = None

                return ret


            df['put_convert_price'] = df['put_convert_price'].map(convert_float)
            df['sprice'] = df['sprice'].map(convert_float)
            df['ration'] = df['ration'].map(convert_percent)
            df['volume'] = df['volume'].map(convert_float)
            df['convert_amt_ratio']=df['convert_amt_ratio'].map(remove_percent)
            df['ration_rt']=df['ration_rt'].map(convert_float)

            rename_columns = {'bond_id': '可转债代码', 'bond_nm': '可转债名称', 'price': '可转债价格','stock_nm': '正股名称',
                              'stock_cd': '正股代码',
                              'sprice': '正股现价',
                              'sincrease_rt': '正股涨跌幅',
                              'convert_price': '最新转股价', 'premium_rt': '溢价率', 'increase_rt': '可转债涨幅',
                              'put_convert_price': '回售触发价', 'convert_dt': '转股起始日',
                              'short_maturity_dt': '到期时间', 'volume': '成交额(万元)',
                               'redeem_price': '强赎价格', 'year_left': '剩余时间',
                              'next_put_dt': '回售起始日', 'rating_cd': '评级', 'issue_dt': '发行时间', 'redeem_tc': '强制赎回条款',
                              'adjust_tc': '下修条件', 'adjust_tip': '下修提示', 'put_tc': '回售', 'adj_cnt': '下调次数',
                            #   'ration':'已转股比例'
                              'convert_amt_ratio':'转债剩余占总市值比',
                            'curr_iss_amt':'剩余规模','orig_iss_amt':'发行规模',
                            'ration_rt':'股东配售率',
                              }

            df = df.rename(columns=rename_columns)
            df=df[list(rename_columns.values())]
            df['更新日期'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

        # dfx = df[['可转债代码', '可转债名称', '可转债涨幅', '可转债价格', '正股名称', '正股代码',
        #           '正股涨跌幅', '正股现价', '最新转股价', '溢价率', '评级',
        #           '转股起始日', '回售起始日', '回售触发价', '剩余时间',
        #           '更新日期']]

        df = df.set_index('可转债代码',drop=True)
        try:
            df.to_sql('tb_bond_jisilu', engine, if_exists='replace',dtype={'可转债代码':VARCHAR(10)})
        except Exception as e:
            logger.info(e)


def main():
    logger.info('Start')
    obj = Jisilu()
    obj.dataframe()


if __name__ == '__main__':
    if is_holiday():
        logger.info("Holidy")
        exit()
    main()
