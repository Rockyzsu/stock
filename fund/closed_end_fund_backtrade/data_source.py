import json
import sys
import akshare as ak
import pandas as pd

sys.path.append('../../')
from configure.settings import DBSelector

# 封基回撤

# mongo get fund code

class DataSource():

    def __init__(self):
        self.mongo_client = DBSelector().mongo('qq')
        self.doc = self.mongo_client['closed_end_fund']['2022-02-28']
        self.bt_doc = self.mongo_client['db_stock']['closed_end_fund']

    def get_fund_code(self):
        codes = []
        for code in self.doc.find({}, {'fund_id': 1, '_id': 0}):
            codes.append(code['fund_id'])
        return codes

    def all_market_data(self):
        '''
        获取数据
        '''
        for code in self.get_fund_code():
            df = self.get_closed_fund_netvalue(code)
            # df = self.get_net_value(code)
            df['code']=code
            df['净值日期']=df['净值日期'].astype(str)
            self.df_into_mongo(df)

    def df_into_mongo(self, df):
        data_list = df.to_json(orient='records', force_ascii=False)
        data_list = json.loads(data_list)
        try:
            self.bt_doc.insert_many(data_list)
        except Exception as e:
            print(e)

    def get_net_value(self,code):
        '''
        获取基金的净值
        '''
        fund_open_fund_info_em_df = ak.fund_open_fund_info_em(fund=code, indicator="单位净值走势")
        return fund_open_fund_info_em_df

    def get_closed_fund_netvalue(self,code):
        fund_etf_fund_info_em_df = ak.fund_etf_fund_info_em(fund=code)
        return fund_etf_fund_info_em_df

    def get_data_from_mongo(self):
        result = []
        for item in self.bt_doc.find({},{'_id':0}):
            result.append(item)
        df= pd.DataFrame(result)
        return df


