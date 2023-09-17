# 暂停申购的基金
import datetime
import sys
sys.path.append('..')
from configure.util import send_message_via_wechat,is_weekday_today
from configure.settings import DBSelector
import pandas as pd
import requests
import demjson

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6',
    'Referer': 'http://fund.eastmoney.com/HH_jzzzl.html',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
}

mapper = {'lof':8,'qdii':6}
cookies = {
    'qgqp_b_id': '613083479b0a0e85cff3fc668cfd26ea',
    'mtp': '1',
    'ct': 'AAg2I3p6vBNVbq9JXnqvYYNJnSSTtLmlB_L3-rt4gW7nTU2nNJRVgRd-bmzw0xqTyTiO64OpbJ0ytLSgLAlkg6pFla3UGEuIAlqZbY7U9lJ2l-tlQ62uRRf08x8ObnhgW2Gecs-xS74dNFza2NUQHQe21nAwVxC3KSa2TTTfA9k',
    'ut': 'FobyicMgeV52Ad4fCxim_H1USOAH2Xm1YM92wqcPQxLzEfFPyFgALYPBNjAWe11vwFJMDDUgbUeakhrr5gkoHiMO9BHZpsgY0PM4ZE67fDEFx_5Sol0sbtwFlqqb1mwGSqt9Tg7H6EXBbmb4nHyFdQnQXrjIXbqYckVu6-tPdGioP8WnUZtF6iIgiBphOYuGyg5g83iA3KQzZIcJBbocRLgwbJUY5TRbRsL_EwEd_pbc0eQWFFSli-yKuYFXnezjcnHZBV4ig4uP4yQs-WNnoBE1Y2AqA1gk',
    'pi': '6590645210394316%3bk6590645210394316%3b%e5%8f%af%e8%bd%ac%e5%80%ba%e9%87%8f%e5%8c%96%e5%88%86%e6%9e%90%3bv2fMOy74x0b0%2fP%2b1n8jNmRRko8sGBLDXRAPZzqn7zdwseSdYB%2bHgLI1Qwtldp5xlFXYj8RlzrWy7XLL4Jgrtx7gDjCcmCG%2bwwB09Jkf6n3dbGfm4eHEQpYA%2b46tj0jUL3UfHRfr1c3wWFFdITTvk6M6qaLzHo1IJT0jnl2IEomTj6KgRZbq8ffXyCSJhaoJuP3CBuYo4%3b1dpLFwCAxxJm9AfI8kFhD0ECSrD234b2cXEDviN9FfkFNNONh7Bq%2bnJQ8Ki1skgnKHD2A9RQ0PoqhCkLKHzACpdk%2b2XmzIPuG9YXz9pNo9wOstx41mYli70dYnbgMM3sKm0bn0WzYrIIZXWyrMtlcMr3y1R%2bzA%3d%3d',
    'uidal': '6590645210394316%e5%8f%af%e8%bd%ac%e5%80%ba%e9%87%8f%e5%8c%96%e5%88%86%e6%9e%90',
    'sid': '122139003',
    'vtpst': '|',
    'EmFundFavorVersion2': '0',
    'st_si': '67006181870113',
    'emshistory': '%5B%22161128%22%5D',
    'HAList': 'ty-0-161128-%u6807%u666E%u4FE1%u606F%u79D1%u6280LOF%2Cty-0-123096-%u601D%u521B%u8F6C%u503A%2Cty-1-688570-%u5929%u739B%u667A%u63A7%2Cty-116-00293-%u56FD%u6CF0%u822A%u7A7A%2Cty-105-WLGS-%u5B8F%u5229%u8425%u9020%2Cty-105-NIU-%u5C0F%u725B%u7535%u52A8%2Cty-0-000070-%u7279%u53D1%u4FE1%u606F',
    'ASP.NET_SessionId': '5xsk0luksl1mxpthkcmmhfms',
    'st_asi': 'delete',
    'st_pvi': '30849193689390',
    'st_sp': '2022-02-19%2022%3A30%3A59',
    'st_inirUrl': 'https%3A%2F%2Ffund.eastmoney.com%2F',
    'st_sn': '32',
    'st_psi': '20230628184744669-118000300904-1111826291',
}
class FundPurchaseEm:
    today = datetime.datetime.today().strftime('%Y-%m-%d')

    def fund_purchase_em(self,types) -> pd.DataFrame:
        """
        东方财富网站-天天基金网-基金数据-基金申购状态
        https://fund.eastmoney.com/Fund_sgzt_bzdm.html#fcode,asc_1
        :return: 基金申购状态
        :rtype: pandas.DataFrame
        """
        url = "http://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        }
        args = mapper.get(types,1)

        params = {
            "t": "1",
            "lx": str(args),
            "page": "1,50000",
            "js": "db",
            "sort": "fcode,asc",
            "_": "1641528557742",
        }

        MAX_COUNT = 10

        for i in range(MAX_COUNT):
            try:
                r = requests.get(url, params=params, headers=headers,cookies=cookies)
            except Exception as e:
                print(e)
                continue
            else:
                break

        if i == MAX_COUNT - 1:
            send_message_via_wechat("{} 获取基金申购失败！".format(self.today))
            raise ValueError('MAX_COUNT times retry failed')


        data_text = r.text
        # print(data_text)
        try:
            data_json = demjson.decode(data_text.strip("var db="))
        except Exception as e:
            print(data_text)
            send_message_via_wechat("{} 获取基金申购失败！ 解析出错".format(self.today))
            raise ValueError('MAX_COUNT times retry failed')

        temp_df = pd.DataFrame(data_json["datas"])
        temp_df.reset_index(inplace=True)
        temp_df["index"] = temp_df.index + 1
        temp_df.columns = [
            "序号",
            "基金代码",
            "基金简称",
            "拼音",
            "今日单位净值",
            "今日累计净值",
            "昨日单位净值",
            "昨日累计净值",
            "日增长值",
            "日增长率",
            "申购状态",
            "赎回状态",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10"
        ]
        temp_df = temp_df[
            [

                "基金代码",
                "基金简称",
                "拼音",
                "今日单位净值",
                "今日累计净值",
                "昨日单位净值",
                "昨日累计净值",
                "日增长值",
                "日增长率",
                "申购状态",
                "赎回状态",
            ]
        ]
        temp_df['类别']=types
        temp_df['更新时间']=datetime.datetime.now()

        return temp_df

    def run(self):
        if not is_weekday_today():
            return
        for k,v in mapper.items():
            data = self.fund_purchase_em(k)
            data.to_excel('../data/{}-基金申购状态-{}.xlsx'.format(self.today,k), encoding='utf8')
            engine = DBSelector().get_engine('db_fund_purchase','qq')
            data.to_sql('fund_purchase_{}'.format(self.today), engine, index=False, if_exists='append')

if __name__ == '__main__':
    app = FundPurchaseEm()
    app.run()
