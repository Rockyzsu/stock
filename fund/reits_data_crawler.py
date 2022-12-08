import datetime
import requests
import pandas as pd
import sys
sys.path.append('..')
from configure.util import send_message_via_wechat

today = datetime.datetime.now().strftime('%Y-%m-%d')


def reits_realtime_em() -> pd.DataFrame:
    """
    东方财富网-行情中心-REITs-沪深 REITs
    http://quote.eastmoney.com/center/gridlist.html#fund_reits_all
    :return: 沪深 REITs-实时行情
    :rtype: pandas.DataFrame
    """
    url = "http://95.push2.eastmoney.com/api/qt/clist/get"
    params = {
        "pn": "1",
        "pz": "80",
        "po": "1",
        "np": "1",
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": "2",
        "invt": "2",
        "fid": "f3",
        "fs": "m:1 t:9 e:97,m:0 t:10 e:97",
        "fields": "f2,f3,f4,f5,f6,f12,f14,f15,f16,f17,f18",
        "_": "1630048369992",
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    temp_df = pd.DataFrame(data_json["data"]["diff"])
    temp_df.reset_index(inplace=True)
    temp_df["index"] = range(1, len(temp_df) + 1)
    temp_df.rename(
        {
            "index": "序号",
            "f2": "最新价",
            "f3": "涨跌幅",
            "f4": "涨跌额",
            "f5": "成交量",
            "f6": "成交额",
            "f12": "代码",
            "f14": "名称",
            "f15": "最高价",
            "f16": "最低价",
            "f17": "开盘价",
            "f18": "昨收",
        },
        axis=1,
        inplace=True,
    )
    temp_df = temp_df[
        [
            "序号",
            "代码",
            "名称",
            "最新价",
            "涨跌额",
            "涨跌幅",
            "成交量",
            "成交额",
            "开盘价",
            "最高价",
            "最低价",
            "昨收",
        ]
    ]
    return temp_df

def get_reits_data():
    msg = '从ak获取reits出错'

    try:
        reits_realtime_em_df = reits_realtime_em()
    except Exception as e:
        send_message_via_wechat(msg)
    else:
        if len(reits_realtime_em_df)==0:
            send_message_via_wechat(msg)
        else:
            from configure.settings import DBSelector
            engine = DBSelector().get_engine('db_reits','tencent-1c')
            reits_realtime_em_df.to_sql('reits-{}'.format(today),con=engine)

if __name__=='__main__':
    get_reits_data()