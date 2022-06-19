import sys
sys.path.append('..')
from configure.settings import get_tushare_pro
pro = get_tushare_pro()
# pro = ts.pro_api()

# df = pro.index_weight(index_code='399300.SZ', start_date='20180901', end_date='20180930') board
df = pro.index_global(ts_code='XIN9', start_date='20200201', end_date='20200220')
print(df)