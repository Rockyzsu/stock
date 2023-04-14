import datetime
import time

import akshare as ak
import pandas as pd

symbol_dict =  {"股票型", "混合型", "指数型", "QDII", "LOF",}
import sys
sys.path.append('..')
from configure.settings import DBSelector
import pymongo

def get_mongo_doc():
    client = DBSelector().mongo('qq')
    doc = client['db_stock']['stock_holder_2023-04-14']
    try:
        doc.create_index([("基金代码", pymongo.ASCENDING)],unique=True)
    except Exception as e:
        print(e)
    return doc

def get_mongo_target_doc():
    client = DBSelector().mongo('qq')
    doc = client['db_stock']['stock_holder_2023-04-14_top10']
    # try:
    #     doc.create_index([("基金代码", pymongo.ASCENDING)],unique=True)
    # except Exception as e:
    #     print(e)
    return doc


def insert_one(doc,data):
    code = data['基金代码']
    if not doc.find_one({'基金代码':code}):
        doc.insert_one(data)



def get_basic_info():
    doc = get_mongo_doc()

    for item in symbol_dict:
        fund_open_fund_rank_em_df = ak.fund_open_fund_rank_em(symbol=item)
        print(fund_open_fund_rank_em_df.head())
        print(item,len(fund_open_fund_rank_em_df))
        obj_list = fund_open_fund_rank_em_df.to_dict('records')
        for item in obj_list:
            insert_one(doc,item)


def find_top_holding_stock(code):
    import akshare as ak
    try:
        fund_portfolio_hold_em_df = ak.fund_portfolio_hold_em(symbol=code, date="2022")
        # print(fund_portfolio_hold_em_df)
    except Exception as e:
        return None
    else:
        return fund_portfolio_hold_em_df

def latest_holding(code):
    four_season = '2022年4季度股票投资明细'
    three_season = '2022年3季度股票投资明细'

    df = find_top_holding_stock(code)
    if df is not None:
        if len(df) > 0:
            df['基金代码']=code
            tmp_df = df[df['季度'] == four_season]
            tmp2_df = df[df['季度'] == three_season]

            if len(tmp_df) > 0:
                return tmp_df
            elif len(tmp2_df) > 0:
                return tmp2_df
            else:
                return None

def get_fund_code():
    doc = get_mongo_doc()
    target = get_mongo_target_doc()

    all_code = doc.find({},{'基金代码':1})
    df_list=[]
    for _code in all_code:
        if target.find_one({'基金代码':_code}):
            continue
        code=_code['基金代码']
        df = latest_holding(code)
        if df is None:
            print('df is empty')
            continue
        df['updated']=datetime.datetime.now()

        obj_list = df.to_dict('records')
        target.insert_many(obj_list)

    df_fund = pd.concat(df_list)
    obj_list = df_fund.to_dict('records')
    for item in obj_list:
        target.insert_one(item)

def run():
    get_fund_code()

if __name__ == '__main__':
    run()