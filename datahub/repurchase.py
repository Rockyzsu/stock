import os
import sys
import pandas as pd
import numpy as np
import xcsc_tushare as xc

sys.path.append('..')
from configure.settings import config_dict

xc_server = config_dict()['xc_server']
xc_token_pro = config_dict()['xc_token_pro']

xc.set_token(xc_token_pro)
pro = xc.pro_api(env='prd', server=xc_server)

df = pro.repurchase(ann_date='', start_date='20210201', end_date='20210301')
df['ts_code']=df['ts_code'].map(lambda x:x.split('.')[0])
ROOT_PATH = r'C:\git\stock\data'
excel_file = os.path.join(ROOT_PATH, 'tb_bond_jisilu.xlsx')
jsl_data = pd.read_excel(excel_file,dtype={'正股代码':np.str})

# print(jsl_data)
# 这个接口失效了
# df = pro.stk_account(start_date='20210101', end_date='20211030')
# print(df)
merge_table = pd.merge(df,jsl_data,left_on='ts_code',right_on='正股代码')
# print(merge_table.head())
print(len(merge_table))
print(merge_table)