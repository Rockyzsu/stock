import pandas
import pandas as pd

df = pd.read_excel('../回售.xlsx')
# print(df)
hit_recall_df = df[df['最新转股价']<df['回售触发价']]
hit_recall_df=hit_recall_df[(hit_recall_df['可转债价格']<120)&(hit_recall_df['剩余时间']<3)]
target = hit_recall_df.sort_values('剩余时间')
target.to_excel('target-回售.xlsx',encoding='utf8')