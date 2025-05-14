# 东财涨停板
import sys

sys.path.append('..')
import datetime
import pandas as pd
import requests
import re
from configure.util import send_message_via_wechat
from configure.settings import DBSelector

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Pragma': 'no-cache',
    'Referer': 'https://quote.eastmoney.com/ztb/detail',
    'Sec-Fetch-Dest': 'script',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"'
}


def get_ut_value():
    url = 'https://quote.eastmoney.com/ztb/newstatic/build/detail.js'
    req = requests.get(url, headers=headers)
    text = req.text
    match = re.search('{ut:"(\w+)",', text)
    if match:
        return match.group(1)
    else:
        return None


ut = get_ut_value()
if ut is None:
    send_message_via_wechat('eastmoney ut None')
    raise ValueError('ut is None')


def stock_zt_pool_em(date: str = "20241008") -> pd.DataFrame:
    """
    东方财富网-行情中心-涨停板行情-涨停股池
    https://quote.eastmoney.com/ztb/detail#type=ztgc
    :param date: 交易日
    :type date: str
    :return: 涨停股池
    :rtype: pandas.DataFrame
    """

    url = "https://push2ex.eastmoney.com/getTopicZTPool"
    params = {
        "ut": ut,
        "dpt": "wz.ztzt",
        "Pageindex": "0",
        "pagesize": "10000",
        "sort": "fbt:asc",
        "date": date,
    }
    r = requests.get(url, params=params, headers=headers)
    data_json = r.json()
    if data_json["data"] is None:
        return pd.DataFrame()
    if len(data_json["data"]["pool"]) == 0:
        return pd.DataFrame()
    temp_df = pd.DataFrame(data_json["data"]["pool"])
    temp_df.reset_index(inplace=True)
    temp_df["index"] = range(1, len(temp_df) + 1)
    temp_df.columns = [
        "序号",
        "代码",
        "_",
        "名称",
        "最新价",
        "涨跌幅",
        "成交额",
        "流通市值",
        "总市值",
        "换手率",
        "连板数",
        "首次封板时间",
        "最后封板时间",
        "封板资金",
        "炸板次数",
        "所属行业",
        "涨停统计",
    ]
    temp_df["涨停统计"] = (
            temp_df["涨停统计"].apply(lambda x: dict(x)["days"]).astype(str)
            + "/"
            + temp_df["涨停统计"].apply(lambda x: dict(x)["ct"]).astype(str)
    )
    temp_df = temp_df[
        [
            "序号",
            "代码",
            "名称",
            "涨跌幅",
            "最新价",
            "成交额",
            "流通市值",
            "总市值",
            "换手率",
            "封板资金",
            "首次封板时间",
            "最后封板时间",
            "炸板次数",
            "涨停统计",
            "连板数",
            "所属行业",
        ]
    ]
    temp_df["首次封板时间"] = temp_df["首次封板时间"].astype(str).str.zfill(6)
    temp_df["最后封板时间"] = temp_df["最后封板时间"].astype(str).str.zfill(6)
    temp_df["最新价"] = temp_df["最新价"] / 1000
    temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"], errors="coerce")
    temp_df["最新价"] = pd.to_numeric(temp_df["最新价"], errors="coerce")
    temp_df["成交额"] = pd.to_numeric(temp_df["成交额"], errors="coerce")
    temp_df["流通市值"] = pd.to_numeric(temp_df["流通市值"], errors="coerce")
    temp_df["总市值"] = pd.to_numeric(temp_df["总市值"], errors="coerce")
    temp_df["换手率"] = pd.to_numeric(temp_df["换手率"], errors="coerce")
    temp_df["封板资金"] = pd.to_numeric(temp_df["封板资金"], errors="coerce")
    temp_df["炸板次数"] = pd.to_numeric(temp_df["炸板次数"], errors="coerce")
    temp_df["连板数"] = pd.to_numeric(temp_df["连板数"], errors="coerce")
    return temp_df


def stock_zt_pool_strong_em(date: str = "20241231") -> pd.DataFrame:
    """
    东方财富网-行情中心-涨停板行情-强势股池
    https://quote.eastmoney.com/ztb/detail#type=qsgc
    :param date: 交易日
    :type date: str
    :return: 强势股池
    :rtype: pandas.DataFrame
    """
    url = "https://push2ex.eastmoney.com/getTopicQSPool"
    params = {
        "ut": ut,
        "dpt": "wz.ztzt",
        "Pageindex": "0",
        "pagesize": "5000",
        "sort": "zdp:desc",
        "date": date,
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    if data_json["data"] is None:
        return pd.DataFrame()
    if len(data_json["data"]["pool"]) == 0:
        return pd.DataFrame()
    temp_df = pd.DataFrame(data_json["data"]["pool"])
    temp_df.reset_index(inplace=True)
    temp_df["index"] = range(1, len(temp_df) + 1)
    temp_df.columns = [
        "序号",
        "代码",
        "_",
        "名称",
        "最新价",
        "涨停价",
        "_",
        "涨跌幅",
        "成交额",
        "流通市值",
        "总市值",
        "换手率",
        "是否新高",
        "入选理由",
        "量比",
        "涨速",
        "涨停统计",
        "所属行业",
    ]
    temp_df["涨停统计"] = (
            temp_df["涨停统计"].apply(lambda x: dict(x)["days"]).astype(str)
            + "/"
            + temp_df["涨停统计"].apply(lambda x: dict(x)["ct"]).astype(str)
    )
    temp_df = temp_df[
        [
            "序号",
            "代码",
            "名称",
            "涨跌幅",
            "最新价",
            "涨停价",
            "成交额",
            "流通市值",
            "总市值",
            "换手率",
            "涨速",
            "是否新高",
            "量比",
            "涨停统计",
            "入选理由",
            "所属行业",
        ]
    ]
    temp_df["最新价"] = temp_df["最新价"] / 1000
    temp_df["涨停价"] = temp_df["涨停价"] / 1000
    explained_map = {1: "60日新高", 2: "近期多次涨停", 3: "60日新高且近期多次涨停"}
    temp_df["入选理由"] = temp_df["入选理由"].apply(lambda x: explained_map[x])
    temp_df["是否新高"] = temp_df["是否新高"].apply(lambda x: "是" if x == 1 else "否")
    temp_df["涨跌幅"] = pd.to_numeric(temp_df["涨跌幅"], errors="coerce")
    temp_df["最新价"] = pd.to_numeric(temp_df["最新价"], errors="coerce")
    temp_df["涨停价"] = pd.to_numeric(temp_df["涨停价"], errors="coerce")
    temp_df["成交额"] = pd.to_numeric(temp_df["成交额"], errors="coerce")
    temp_df["流通市值"] = pd.to_numeric(temp_df["流通市值"], errors="coerce")
    temp_df["总市值"] = pd.to_numeric(temp_df["总市值"], errors="coerce")
    temp_df["换手率"] = pd.to_numeric(temp_df["换手率"], errors="coerce")
    temp_df["涨速"] = pd.to_numeric(temp_df["涨速"], errors="coerce")
    temp_df["量比"] = pd.to_numeric(temp_df["量比"], errors="coerce")
    return temp_df


def stock_zt_pool_zbgc_em(date: str = "20241011") -> pd.DataFrame:
    """
    东方财富网-行情中心-涨停板行情-炸板股池
    https://quote.eastmoney.com/ztb/detail#type=zbgc
    :param date: 交易日
    :type date: str
    :return: 炸板股池
    :rtype: pandas.DataFrame
    """
    thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)
    thirty_days_ago_str = thirty_days_ago.strftime("%Y%m%d")
    if int(date) < int(thirty_days_ago_str):
        raise ValueError("炸板股池只能获取最近 30 个交易日的数据")

    url = "https://push2ex.eastmoney.com/getTopicZBPool"
    params = {
        "ut": ut,
        "dpt": "wz.ztzt",
        "Pageindex": "0",
        "pagesize": "5000",
        "sort": "fbt:asc",
        "date": date,
    }
    r = requests.get(url, params=params)
    data_json = r.json()
    if data_json["data"] is None:
        return pd.DataFrame()
    if len(data_json["data"]["pool"]) == 0:
        return pd.DataFrame()
    temp_df = pd.DataFrame(data_json["data"]["pool"])
    temp_df.reset_index(inplace=True)
    temp_df["index"] = range(1, len(temp_df) + 1)
    temp_df.columns = [
        "序号",
        "代码",
        "_",
        "名称",
        "最新价",
        "涨停价",
        "涨跌幅",
        "成交额",
        "流通市值",
        "总市值",
        "换手率",
        "首次封板时间",
        "炸板次数",
        "振幅",
        "涨速",
        "涨停统计",
        "所属行业",
    ]
    temp_df["涨停统计"] = (
            temp_df["涨停统计"].apply(lambda x: dict(x)["days"]).astype(str)
            + "/"
            + temp_df["涨停统计"].apply(lambda x: dict(x)["ct"]).astype(str)
    )
    temp_df = temp_df[
        [
            "序号",
            "代码",
            "名称",
            "涨跌幅",
            "最新价",
            "涨停价",
            "成交额",
            "流通市值",
            "总市值",
            "换手率",
            "涨速",
            "首次封板时间",
            "炸板次数",
            "涨停统计",
            "振幅",
            "所属行业",
        ]
    ]
    temp_df["最新价"] = temp_df["最新价"] / 1000
    temp_df["涨停价"] = temp_df["涨停价"] / 1000
    temp_df["首次封板时间"] = temp_df["首次封板时间"].astype(str).str.zfill(6)
    return temp_df


def data_dump(df, table_name):
    engine = DBSelector().get_engine('db_zdt', 'qq')
    df.to_sql(table_name, con=engine, if_exists='replace', index=False)


def main():
    date = datetime.datetime.now().strftime('%Y%m%d')
    zt_df = stock_zt_pool_em(date)
    data_dump(zt_df, 'zt_' + date)

    strong_df = stock_zt_pool_strong_em(date)
    data_dump(strong_df, 'strong_' + date)

    break_df = stock_zt_pool_zbgc_em(date)
    data_dump(break_df, 'break_' + date)

if __name__ == '__main__':
    main()
