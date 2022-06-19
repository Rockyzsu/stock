# 获取基金的基本信息

import akshare as ak
import datetime
import fire
import re
import numpy as np
import pyecharts.options as opts
from pyecharts.charts import Line
from pyecharts import options as opts

# 计算基金的收益率曲线
code_list = [{'code': '008331', 'name': '万家可转债债券A'}, {'code': '000297', 'name': '鹏华可转债'}, {'code': '006482', 'name': '广发可转债债券A'}, {'code': '000536', 'name': '前海开源可转债债券'}, {'code': '310518', 'name': '申万菱信可转债债券A'}, {'code': '240018', 'name': '华宝可转债债券'}, {'code': '340001', 'name': '兴全可转债混合'}, {'code': '005273', 'name': '华商可转债A'}, {'code': '470058', 'name': '汇添富可转换债券A'}, {'code': '110035', 'name': '易方达双债增强A'}, {'code': '008809', 'name': '安信民稳增长混合A'}, {'code': '005876', 'name': '易方达鑫转增利混合A'}, {'code': '006102', 'name': '浙商丰利增强债券'}, {'code': '003092', 'name': '华商丰利增强定开债A'}]
def parse_fund_code_in_txt(filename):

    with open(filename,encoding='utf8') as fp:
        lines = fp.readlines()
    code_list = []
    for line in lines:
        match = re.search('\(F(\d+)\)',line)

        if match:
            name_match = re.search('\$(.*?)\(',line).group(1)
            code_list.append({'code':match.group(1),'name':name_match})

    return code_list

def convert_time(x):
    return str(x).replace(' 00:00:00','')
    


def get_net_value(code):
    '''
    获取基金的净值
    '''
    fund_open_fund_info_em_df = ak.fund_open_fund_info_em(fund=code, indicator="累计净值走势")
    return fund_open_fund_info_em_df


def get_year(start,end):
    '''
    获取年份
    '''
    year = (datetime.datetime.strptime(end,'%Y-%m-%d')- datetime.datetime.strptime(start,'%Y-%m-%d')).days/365
    return year


def get_profit_rate(df):
    '''
    计算所有的收益率
    '''
    return round((df['累计净值'].iloc[-1]-df['累计净值'].iloc[0])/df['累计净值'].iloc[0],2)


def get_yearly_profit_rate(df):
    '''
    计算年化收益率
    '''
    
    start = str(df['净值日期'].iloc[0])
    end = str(df['净值日期'].iloc[-1])
    year = get_year(start,end)
    print('开始时间：',start)
    print('成立年数：',round(year,2),'年')
    profit = get_profit_rate(df)
    print('成立以来累积收益率:',profit)
    year_profit = (1+profit)**(1/year)-1
    return start,round(year,2),profit,round(year_profit,2)



def fund_profit(code,name=''):
    '''
    生成字典
    '''
    df = get_net_value(code)
    max_withdraw,max_date_index = get_max_withdraw(df['累计净值'].tolist())
    start,year,profit,year_profit = get_yearly_profit_rate(df)
    d={}
    d['代码']=code
    d['名称']=name
    d['发行日期']=start
    d['成立年数']=year
    d['累积收益率']=profit
    d['年化收益率']=year_profit
    d['最大回撤']=max_withdraw
    return d


def automatic_investment_plan(code):
    '''
    定投收益
    '''
    df = get_net_value(code)

    money = 10000
    total_share =0 
    interval = 22
    length = len(df)
    sum_money=0
    count=0
    for i in range(0,length,interval):
        buy_date_df = df.iloc[i]
        share = money/buy_date_df['累计净值']
        total_share+=share
        sum_money+=money
        count+=1
    virtual_profit = (df.iloc[-1]['累计净值']*total_share-sum_money)/sum_money
    data=[]
    year,month,day=str(df.iloc[0]['净值日期']).split('-')
    for i in range(count):
        data.append((datetime.date(int(year), int(month), int(day))+datetime.timedelta(days=i*30), -1*money))
    current_money = df.iloc[-1]['累计净值']*total_share
    data.append((datetime.date(int(year), int(month), int(day))+datetime.timedelta(days=i*30),current_money))
    percent = xirr(data)
    every_round_profit = irr([money]*count+[-1*current_money])
    real_profit = pow(every_round_profit+1,count)-1
    return code,sum_money,round(current_money,2),round(percent,4),round(virtual_profit,4),round(real_profit,4)



def xirr(cashflows):
    # 函数
    years = [(ta[0] - cashflows[0][0]).days / 365. for ta in cashflows]
    residual = 1.0
    step = 0.05
    guess = 0.05
    epsilon = 0.0001
    limit = 10000
    while abs(residual) > epsilon and limit > 0:
        limit -= 1
        residual = 0.0
        for i, trans in enumerate(cashflows):
            residual += trans[1] / pow(guess, years[i])
        if abs(residual) > epsilon:
            if residual > 0:
                guess += step
            else:
                guess -= step
                step /= 2.0
    return guess - 1


def irr(values):
    res = np.roots(values[::-1])  # 求根，对于n次多项式，p[0] * x**n + p[1] * x**(n-1) + ... + p[n-1]*x + p[n]，传入p的列表参数[p[0],p[1],...p[n]].
    mask = (res.imag == 0) & (res.real > 0)  # 虚部为0，实部为非负数。
    if not mask.any():  # 判断是否有满足条件的实根
        return np.nan  # 不满足，返回Not A Number
    res = res[mask].real
    # NPV(rate) = 0 can have more than one solution so we return
    # only the solution closest to zero.
    rate = 1/res - 1  # 这里解出的res，也就是符合条件的x，其实等于1/(1+r)，因此要做一个变换回去，r=1/x-1
    rate = rate.item(np.argmin(np.abs(rate)))  # argmin()取最小值的下标，也就是说可能会计算出多个折现率，我们取最小那个
    return rate


def get_max_withdraw(indexs):
    max_withdraw = 0
    start_date_index =0
    max_date_index =0
    last_high = indexs[0]
    
    for index,current in enumerate(indexs):
        # 遍历所有数据
        if current>last_high:
            last_high=current
            # start_date_index=index
            continue

        if (last_high-current)/last_high>max_withdraw:
            # 找到一个最大值时，保存其位置
            max_withdraw = (last_high-current)/last_high
            max_date_index=index

    return max_withdraw,max_date_index # 变成百分比



def plot_profit_line(df,code,name=""):
    title="{}-{}-基金收益率曲线".format(code,name)
    X=df['净值日期'].tolist()
    Y=list(map(lambda x:round(x,2),df['累计净值'].tolist()))
    c = (
        Line()
        .add_xaxis(X)
        .add_yaxis('', Y, is_smooth=True,
            label_opts=opts.LabelOpts(is_show=False),
            linestyle_opts=opts.LineStyleOpts(width=1,color='rgb(255, 0, 0)'),
        ).set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            xaxis_opts=opts.AxisOpts(
                                    name='日期',
                                    # min_interval=5,
                                    splitline_opts=opts.SplitLineOpts(is_show=True),
                                            axislabel_opts=opts.LabelOpts(rotate=45),

                                    ),
            yaxis_opts=opts.AxisOpts(
                                    min_=round(min(Y),2),
                                    max_=round(max(Y),2),
                splitline_opts=opts.SplitLineOpts(is_show=True),
            )
                                        ).set_colors(['green'])
        .render(f"../data/{title}-{name}.html")
    )
    
def draw_profit_curve(code,name):
    df =  get_net_value(code)
    plot_profit_line(df,code,name)


def automatic_investment_plan_result(code):
    code,sum_money,current_money,percent,virtual_profit,real_profit=automatic_investment_plan(code)
    print('每月定投{} 10000元，累计投入 {}, 当前累计本金与收入为{}，定投年化收益率为{}%, xiir计算的累计收益率{}%'.format(code,sum_money,current_money,percent*100,real_profit*100))

def help():
    print('''
    Usage:
    获取基金基本信息：python fund_profit_info.py --code=513050 
    绘制收益率曲线：python fund_profit_info.py --code=513050 --kind=draw 
    基金定投收益率 ：python fund_profit_info.py --code=513050  --kind=plan
    ''')

def main(code='513050',kind='profit'):
    if kind=='profit':
        result = fund_profit(code)
        print(result)
    elif kind=='draw':
        draw_profit_curve(code)
        print('收益率曲线绘制完成')
    elif kind=='plan':
        automatic_investment_plan_result(code)
    else:
        help()

def batch_run_draw():
    # 批量运行
    import pandas as pd
    # df = pd.DataFrame(code_list)

    for _code in code_list:
        draw_profit_curve(_code['code'],_code['name'])
        print('收益率曲线绘制完成')

def batch_run_profit():
    # 批量运行
    import pandas as pd
    # df = pd.DataFrame(code_list)
    result=[]
    for _code in code_list:
        result.append(fund_profit(_code['code'],_code['name']))
        print('收益率')
    df = pd.DataFrame(result)
    df.to_excel('基金收益率.xlsx',encoding='utf8')

if __name__=='__main__':
    # fire.Fire(main)
    # print(parse_fund_code_in_txt('xueqiu_content.txt'))
    # batch_run_profit()
    batch_run_draw()