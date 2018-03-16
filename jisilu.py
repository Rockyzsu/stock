# -*-coding=utf-8-*-
import time
import requests
import pandas as pd
from setting import get_engine
engine = get_engine('db_bond')
class Jisilu():
    def __init__(self):
        self.t = long(time.time() * 1000)
        self.headers = {
            'User-Agent': 'User-Agent:Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'}
        self.post_data = {
            'listed': 'Y',
            'rp': '50'
        }
        self.url='https://www.jisilu.cn/data/cbnew/cb_list/?___jsl=LST___t={}'.format(self.t)


    def download(self, url, retry=5):
        for i in range(retry):
            try:
                r = requests.post(url, data=self.post_data)
                if not r.text or r.status_code !=200:
                    continue
                else:
                    return r
            except Exception,e:
                continue
        return None


    def dataframe(self,adjust_no_use=True):
        js = self.download(self.url)
        if not js:
            return None
        ret=js.json()
        bond_list = ret.get('rows')
        cell_list = []
        for item in bond_list:
            # cell_list.append(item.get('cell'))
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
            del df['convert_cd']
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
            df['premium_rt']=map(lambda x:float(x.replace('%','')),df['premium_rt'])


            df=df.rename(columns={'bond_id':u'可转债代码','bond_nm':u'可转债名称','stock_nm':u'正股名称','sprice':u'正股现价','sincrease_rt':u'正股涨跌幅',
                       'convert_price':u'最新转股价','premium_rt':u'溢价率',
                       'put_convert_price':u'回售 触发价','short_maturity_dt':u'到期时间','volume':u'成交额(万元)'})

        df.to_sql('tb_bonds_jisilu',engine,if_exists='replace')






def main():
    obj=Jisilu()
    obj.dataframe()

if __name__=='__main__':
    main()