import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.naive_bayes import BernoulliNB


# 基于优矿平台
industry_category_df = DataAPI.EquIndustryGet(secID=u"",
                                              ticker=u"",
                                              industryVersionCD=u"010303",
                                              industry=u"",
                                              industryID=u"",
                                              industryID1=u"",
                                              industryID2=u"",industryID3=u"",intoDate=u"20210101",equTypeID=u"",field=u"",pandas="1")

industry_category_df=industry_category_df.drop_duplicates(['ticker'])

industry_category_df=industry_category_df[industry_category_df['ticker'].str.startswith(('3','6','0'))] # 过滤部分B股

industry_category_dict = dict(zip(industry_category_df['ticker'].tolist(),industry_category_df['industryName1'].tolist()))

# 交易日历
beginDate=u"20210101"
endDate=u"20210301"
canlendar_df = DataAPI.TradeCalGet(exchangeCD=u"XSHG",beginDate=beginDate,endDate=endDate,isOpen=u"1",field=u"",pandas="1")
canlendar_index = pd.Index(pd.to_datetime(canlendar_df['calendarDate'].tolist()))

columns_name = list(industry_category_dict.keys())

industry_df = pd.DataFrame(data=np.NAN,index=canlendar_index,columns=columns_name)

def apply_func(x):
    s=pd.Series(map(lambda x:industry_category_dict.get(x),x.index),index=x.index)
    return s


industry_df_ = industry_df.apply(apply_func,axis=1)

ticker_list = list(industry_category_dict.keys())
market_df =DataAPI.MktEqudGet(secID=u"",
	ticker=ticker_list,
	tradeDate=u"",
	beginDate=beginDate,endDate=endDate,isOpen="",
	field=u"tradeDate,ticker,marketValue,closePrice",
	pandas="1")

d1=market_df.set_index(['tradeDate','ticker']).unstack()['marketValue']
lcap_=np.log(d1)

labeled_lcap_ = lcap_.apply(pd.qcut,
                            axis=1,
                            q=5,
                            labels=False,
                           )

closePrice=market_df.set_index(['tradeDate','ticker']).unstack()['closePrice']

mom_ = closePrice/closePrice.shift(5)-1

mom_.dropna(axis=0,inplace=True,how='all')

mom_result = mom_.apply(pd.qcut,axis=1,q=5,labels=False)

closePrice_ = closePrice.sort_index()

pct_change = closePrice_.pct_change()

pct_change.dropna(axis=0,inplace=True,how='all')

label_pct_change = pct_change.copy()
label_pct_change[label_pct_change>0]=1
label_pct_change[label_pct_change<=0]=0


index = pd.to_datetime(label_pct_change.index)

trade_calendar=index
strategy_return = pd.Series(index=trade_calendar)

# 进行策略回测
for i in range(len(trade_calendar)-2):

    # 获取训练对应x，y数据的时间和预测时x，y数据的时间
    train_x_time = trade_calendar[i]
    train_y_time = trade_calendar[i+1]
    predict_x_time = trade_calendar[i+1]
    predict_y_time = trade_calendar[i+2]
    
    train_data = pd.DataFrame(
        {
            'labeled_industry': industry_df_.loc[train_x_time],
            'labeled_lcap': labeled_lcap_.loc[train_x_time]+200,
            'labeled_mom': mom_result.loc[train_x_time]+300,
            'labeled_pct_change':label_pct_change.loc[train_y_time]
        }
    )
    
    train_data.dropna(axis=0, inplace=True, how='any')
    dummy_data1 = pd.get_dummies(train_data['labeled_industry'])
    dummy_data2 = pd.get_dummies(train_data['labeled_lcap'])
    dummy_data3 = pd.get_dummies(train_data['labeled_mom'])
    
    dummy_train_x = pd.concat([dummy_data1, dummy_data2, dummy_data3], axis=1)
        # 模型预测用数据读取
    predict_data = pd.DataFrame(
        {
            'labeled_industry': industry_df_.loc[predict_x_time],
            'labeled_lcap': labeled_lcap_.loc[predict_x_time]+200,
            'labeled_mom': mom_result.loc[predict_x_time]+300,
            'pct_change': label_pct_change.loc[predict_y_time]
        }
    )
    predict_data.dropna(axis=0, inplace=True, how='any')
        #  生成预测用哑变量矩阵
    dummy_predict_data1 = pd.get_dummies(predict_data['labeled_industry'])
    dummy_predict_data2 = pd.get_dummies(predict_data['labeled_lcap'])
    dummy_predict_data3 = pd.get_dummies(predict_data['labeled_mom'])
    
    dummy_predict_x = pd.concat([dummy_predict_data1, dummy_predict_data2, dummy_predict_data3], axis=1)
    character_union = dummy_train_x.columns.union(dummy_predict_x.columns)
    dummy_train_x = dummy_train_x.reindex(columns=character_union, fill_value=0)
    dummy_predict_x = dummy_predict_x.reindex(columns=character_union, fill_value=0)
    
    
    # 训练模型
    clf = BernoulliNB()
    clf.fit(dummy_train_x.values, train_data['labeled_pct_change'].values)
    
        # 进行预测并保存数据
    prediction = clf.predict(dummy_predict_x.values)
    predict_data['prediction'] = prediction
    
        # 计算预测日策略收益率并保存到Series中
    # 有可能某一天所有prediction都为0，
    if predict_data['prediction'].sum() == 0:
        strategy_return[predict_y_time] = 0
    else:
        strategy_return[predict_y_time] = np.average(predict_data['pct_change'], weights=predict_data['prediction'])


        # 收益曲线
plt.figure(figsize=(10,6))
plt.plot((strategy_return+1).cumprod(), label='strategy_return')


