# -*- coding: utf-8 -*-
# @Time : 2021/12/16 11:40
# @File : ttjj_others.py
# @Author : Rocky C@www.30daydo.com
import requests
import datetime
import demjson
def rank_data_crawl(time_interval='3n', ft='all'):
    # 当前日期
    td_str = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
    td_dt = datetime.datetime.strptime(td_str, '%Y-%m-%d')
    # 去年今日
    last_dt = td_dt - datetime.timedelta(days=365)
    last_str = datetime.datetime.strftime(last_dt, '%Y-%m-%d')
    rank_url = 'http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft={0}&rs=&gs=0&sc={1}zf&st=desc&sd={2}&ed={3}&qdii=&tabSubtype=,,,,,&pi=1&pn=10000&dx=1'.format(
        ft, time_interval, last_str, td_str)
    # print(rank_url)
    headers = {}  # 需要配置
    rp = requests.get(rank_url, headers=headers)
    rank_txt = rp.text[rp.text.find('=') + 2:rp.text.rfind(';')]
    # print(rank_txt)
    # 数据
    rank_rawdata = demjson.decode(rank_txt)
    # rawdata_allNum = rank_rawdata['allNum']
    rank_list = []
    for i in rank_rawdata['datas']:
        rank_list.append(i.split(','))
    # print(rank_url, 'rawdata_allNum:{}'.format(rawdata_allNum), sep='\n')
    return rank_list


# 详情页面的抓取
def get_allFund_content(single_fund_url):
    try:
        # print(single_fund_url)
        # if infromation[3] !='理财型' and infromation[3] !='货币型' and infromation[2].endswith('(后端)')==False:
        #     code = infromation[0]
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
        r = requests.get(single_fund_url, headers=headers)
        r.encoding = r.apparent_encoding  # 避免中文乱码
        soup = BeautifulSoup(r.text, 'lxml')
        # # 判断交易状态
        # staticItem = soup.select('.staticItem')[0].get_text()
        # if '终止' in staticItem or '认购' in staticItem:
        #     pass
        # else:
        # 各项指标
        # 基金名、基金类型、单位净值、累计净值、基金规模、成立日、评级、基金涨幅及排名
        # （近1周、近1月、近3月、近6月、今年来、近1年、近2年、近3年）
        fund_code = single_fund_url[26:32]
        # fund_name = re.match('[\u4e00-\u9fffA-Za-z]+', soup.select('.fundDetail-tit > div')[0].get_text()).group()
        fund_name = soup.select('.SitePath > a')[2].get_text()
        unit_netValue = soup.select('.dataItem02 > .dataNums > span.ui-font-large')[0].get_text()
        accumulative_netValue = soup.select('.dataItem03 > .dataNums > span.ui-font-large')[0].get_text()
        fund_info = [i for i in soup.select('div.infoOfFund tr > td')]
        # fund_type1 = fund_info[0].get_text().split('：')[1].strip()
        fund_type = re.search('：[DQI\-\u4e00-\u9fffA]+', fund_info[0].get_text()).group()[1:]
        fund_scale = fund_info[1].get_text().split('：')[1].strip()
        fund_establishmentDate = fund_info[3].get_text().split('：')[1].strip()
        # fund_grade = fund_info[5].get_text().split('：')[1].strip()
        fund_Rdata = soup.select('#increaseAmount_stage > .ui-table-hover div.Rdata ')  # 指数基金多一排，考虑re或者排名倒着写
        fund_1weekAmount = fund_Rdata[0].get_text()
        fund_1monthAmount = fund_Rdata[1].get_text()
        fund_3monthAmount = fund_Rdata[2].get_text()
        fund_6monthAmount = fund_Rdata[3].get_text()
        fund_thisYearAmount = fund_Rdata[4].get_text()
        fund_1yearAmount = fund_Rdata[5].get_text()
        fund_2yearAmount = fund_Rdata[6].get_text()
        fund_3yearAmount = fund_Rdata[7].get_text()
        fund_1weekRank = fund_Rdata[-8].get_text()
        fund_1monthRank = fund_Rdata[-7].get_text()
        fund_3monthRank = fund_Rdata[-6].get_text()
        fund_6monthRank = fund_Rdata[-5].get_text()
        fund_thisYearRank = fund_Rdata[-4].get_text()
        fund_1yearRank = fund_Rdata[-3].get_text()
        fund_2yearRank = fund_Rdata[-2].get_text()
        fund_3yearRank = fund_Rdata[-1].get_text()
        Fund_data = [fund_code, fund_name, fund_type, unit_netValue, accumulative_netValue,
                     fund_scale, fund_establishmentDate,
                     fund_1weekAmount, fund_1monthAmount, fund_3monthAmount, fund_6monthAmount,
                     fund_thisYearAmount, fund_1yearAmount, fund_2yearAmount, fund_3yearAmount,
                     fund_1weekRank, fund_1monthRank, fund_3monthRank, fund_6monthRank, fund_thisYearRank,
                     fund_1yearRank, fund_2yearRank, fund_3yearRank]
        print(Fund_data)
        return Fund_data
    except Exception as e:
        # print('Error:', single_fund_url, str(e))
        logging.exception('Error:', single_fund_url, str(e))


def old_main():
    #  初始化区域
    main1_name = ['基金代码', '基金简称', '缩写', '日期', '单位净值', '累计净值',
                  '日增长率(%)', '近1周增幅', '近1月增幅', '近3月增幅', '近6月增幅', '近1年增幅', '近2年增幅', '近3年增幅',
                  '今年来', '成立来', '成立日期', '购买手续费折扣', '自定义', '手续费原价？', '手续费折后？',
                  '布吉岛', '布吉岛', '布吉岛', '布吉岛']
    # main1_name = ['基金代码', '基金简称', '日期', '单位净值', '累计净值',
    #               '日增长率(%)', '近1周增幅', '近1月增幅', '近3月增幅', '近6月增幅', '近1年增幅', '近2年增幅', '近3年增幅',
    #               '今年来', '成立来', '成立日期']
    main2_name = ['基金代码', '基金简称', '基金类型', '单位净值', '累计净值', '基金规模', '成立日期', \
                  '近1周增幅', '近1月增幅', '近3月增幅', '近6月增幅', '今年来增幅', '近1年增幅', '近2年增幅', '近3年增幅', \
                  '近1周排名', '近1月排名', '近3月排名', '近6月排名', '今年来排名', '近1年排名', '近2年排名', '近3年排名']
    # ########################## 先爬API接口 ###################################
    rawData = rank_data_crawl()
    # 数据清洗
    # 未满三年剔除
    rawData = DataFrame(rawData, columns=main1_name)
    rawData = rawData.loc[rawData['近3年增幅'] != '']
    # 去除无用列
    # # rawData.drop(rawData.columns(['缩写', '购买手续费折扣', '自定义', '手续费原价？', '手续费折后？', '布吉岛'], axis=1))
    # rawData.drop(['缩写', '购买手续费折扣', '自定义', '手续费原价？', '手续费折后？', '布吉岛'], axis=1, inplace=True)
    rawData1 = rawData.iloc[1:15, [0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]]
    # main1_name = main1_name[0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]

    # ########################## 单页面抓取 ###################################
    # 获取抓取的detail网址
    detail_urls_list = ['http://fund.eastmoney.com/{}.html'.format(i) for i in rawData1['基金代码']]
    print('#详情页面的抓取#启动时间：', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    middle = datetime.datetime.now()
    # 多线程
    p = Pool(4)
    all_fund_data = p.map(get_allFund_content, detail_urls_list)
    p.close()
    p.join()
    while None in all_fund_data:
        all_fund_data.remove(None)
    end = datetime.datetime.now()
    print('#详情页面的抓取#用时：', str(end - middle))
    print('程序结束时间：', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    all_fund_data = DataFrame(all_fund_data, columns=main2_name)

    # 表合并
    data_merge = pd.merge(rawData1, all_fund_data, how='left', on='基金代码')

    # 文件储存
    file_content = pd.DataFrame(columns=main1_name, data=rawData)
    file_content.to_csv('rawDATA-{}.csv'.format(time.strftime("%Y-%m-%d", time.localtime())), encoding='gbk')

