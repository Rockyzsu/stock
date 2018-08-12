# -*-coding=utf-8-*-
import time
import datetime
import requests
import pandas as pd
from setting import get_engine
import six


engine = get_engine('db_stock')
from setting import llogger

logger=llogger(__file__)

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
            'rp': '50'
        }
        self.url = 'https://www.jisilu.cn/data/cbnew/cb_list/?___jsl=LST___t={}'.format(self.timestamp)

    def download(self, url, retry=5):
        for i in range(retry):
            try:
                r = requests.post(url, data=self.post_data)
                if not r.text or r.status_code != 200:
                    continue
                else:
                    return r
            except Exception as e:
                logger.info(e)
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
        if adjust_no_use:
            del df['active_fl']
            del df['adq_rating']
            del df['list_dt']
            del df['left_put_year']
            del df['owned']
            del df['put_dt']
            del df['real_force_redeem_price']
            del df['redeem_dt']
            del df['apply_cd']
            del df['force_redeem']
            del df['stock_id']
            del df['full_price']
            del df['pre_bond_id']
            del df['ytm_rt']
            del df['ytm_rt_tax']
            del df['repo_cd']
            del df['last_time']
            del df['pinyin']
            del df['put_real_days']
            del df['price_tips']
            del df['btype']
            del df['repo_valid']
            del df['repo_valid_to']
            del df['repo_valid_from']
            del df['repo_discount_rt']
            del df['adjust_tc']
            del df['cpn_desc']
            del df['market']
            del df['stock_net_value']

            df['premium_rt'] = df['premium_rt'].map(lambda x: float(x.replace('%', '')))
            df['price'] = df['price'].astype('float64')
            # df['sincrease_rt']=df['sincrease_rt'].astype('float64')
            df['convert_price'] = df['convert_price'].astype('float64')
            df['premium_rt'] = df['premium_rt'].astype('float64')
            # df['increase_rt']=df['increase_rt'].astype('float64')
            # df['put_convert_price']=df['put_convert_price'].astype('float64')
            df['redeem_price'] = df['redeem_price'].astype('float64')

            df = df.rename(columns={'bond_id': u'可转债代码', 'bond_nm': u'可转债名称', 'stock_nm': u'正股名称', 'stock_cd': u'正股代码',
                                    'sprice': u'正股现价',
                                    'sincrease_rt': u'正股涨跌幅',
                                    'convert_price': u'最新转股价', 'premium_rt': u'溢价率', 'increase_rt': u'可转债涨幅',
                                    'put_convert_price': u'回售 触发价', 'convert_dt': u'转股起始日',
                                    'short_maturity_dt': u'到期时间', 'volume': u'成交额(万元)',
                                    'price': u'可转债价格', 'redeem_price': u'强赎价格', 'year_left': u'剩余时间'})
            # df = df[[u'可转债代码', u'可转债名称', u'可转债涨幅', u'可转债价格', u'正股名称', u'正股现价', u'正股涨跌幅', u'最新转股价', u'溢价率', u'回售 触发价',
            #          u'到期时间']]
            df[u'更新日期'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        dfx=df[['可转债代码','可转债名称','可转债涨幅','可转债价格','正股名称','正股涨跌幅','正股现价','最新转股价','溢价率','转股起始日','剩余时间','更新日期']]
        try:
            dfx.to_sql('tb_bond_jisilu', engine, if_exists='replace')
        except Exception as e:
            logger.info(e)

def main():
    logger.info('Start')
    obj = Jisilu()
    obj.dataframe()


if __name__ == '__main__':
    main()
