# -*-coding=utf-8-*-

__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''

__doc__='''
复盘数据与流程
'''

from configure.settings import DBSelector
import pandas as pd
import pymongo

pd.set_option('expand_frame_repr', False)
client = pymongo.MongoClient('raspberrypi')
db = client['stock']
doc = db['industry']

today = '2018-05-08'
# TODAY = datetime.datetime.now().strftime('%Y-%m-%d')
# daily_engine = DBSelector().get_engine('db_daily','qq')
daily_df = pd.read_sql(today, daily_engine, index_col='index')

class IndustryFupan:
    '''
    每天板块分析
    '''

    def __init__(self):
        self.engine = DBSelector()

# 保存到mongo
    def save_industry(self):
        try:
            doc.drop()
        except Exception as e:
            print(e)

        engine = get_engine('db_stock')
        basic_df = pd.read_sql('tb_basic_info', engine, index_col='index')
        # print(basic_df)
        for name, group in basic_df.groupby('industry'):
            # print(name, group)
            d = dict()
            d['板块名称'] = name
            d['代码'] = group['code'].values.tolist()
            d['更新日期'] = today
            try:
                # pass
                doc.insert(d)
            except Exception as e:
                print(e)


def hot_industry():
    engine = get_engine('db_stock')
    basic_df = pd.read_sql('tb_basic_info', engine, index_col='index')
    industry_dict = {}
    for name, group in basic_df.groupby('industry'):
        # print(name, group)
        industry_dict[name] = group['code'].values.tolist()

    result = {}
    for k, v in industry_dict.items():
        mean = 0.0
        for i in v:
            try:
                percent = daily_df[daily_df['code'] == i]['changepercent'].values[0]
                name = daily_df[daily_df['code'] == i]['name'].values[0]
            except:
                percent = 0
                name = ''
            # print(i,name,percent)
            mean = mean + float(percent)
        m = round(mean / len(v), 2)
        # print('{} mean : {}'.format(k,m))
        result[k] = m

    all_result = sorted(result.items(), key=lambda x: x[1], reverse=True)

    kind = '元器件'
    select_detail = {}
    for code in industry_dict.get(kind):
        try:
            percent = daily_df[daily_df['code'] == code]['changepercent'].values[0]
        except:
            percent = 0
        try:
            name = daily_df[daily_df['code'] == code]['name'].values[0]
        except:
            name = ''
        select_detail[name] = float(percent)
    print('\n\n{} detail\n'.format(kind))
    select_detail = sorted(select_detail.items(), key=lambda x: x[1], reverse=True)
    for n, p in select_detail:
        print(n, p)


def get_industry():
    industry = {}
    for i in doc.find({}, {'_id': 0}):
        print(i.get('板块名称'))
        industry[i.get('板块名称')] = i.get('代码')
    return industry


def daily_hot_industry():
    industry = get_industry()
    result = {}
    for item, code_list in industry.items():
        for code in code_list:
            mean = 0.0
            try:
                percent = daily_df[daily_df['code'] == code]['changepercent'].values[0]
                name = daily_df[daily_df['code'] == code]['name'].values[0]
            except:
                percent = 0
                name = ''
            # print(i,name,percent)
            mean = mean + float(percent)
        m = round(mean / len(code_list), 2)
        result[item] = m

    all_result = sorted(result.items(), key=lambda x: x[1], reverse=True)
    return all_result


# 保存行业的平均涨幅到mongo
def industry_hot_mongo():
    result = daily_hot_industry()
    collection = db['industry_rank']
    collection.drop()
    for item in result:
        d = {}
        d['板块'] = item[0]
        d['涨跌幅'] = item[1]
        d['日期'] = today
        try:
            collection.insert(d)
        except Exception as e:
            print(e)


def industry_detail(kind):
    select_detail = {}
    industry_list = get_industry()
    for code in industry_list.get(kind):
        try:
            percent = daily_df[daily_df['code'] == code]['changepercent'].values[0]
        except:
            percent = 0
        try:
            name = daily_df[daily_df['code'] == code]['name'].values[0]
        except:
            name = ''
        select_detail[name] = float(percent)

    print('\n\n{} detail\n'.format(kind))
    select_detail = sorted(select_detail.items(), key=lambda x: x[1], reverse=True)
    for n, p in select_detail:
        print(n, p)


if __name__ == "__main__":
    # save_industry()
    # hot_industry()
    # get_industry()
    # daily_hot_industry()
    # industry_hot_mongo()
    industry_detail('电器连锁')
