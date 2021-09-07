### 更好的帮助自己炒股(亏钱-。-)
#### 2021-01-28 更新

目前正在重构项目代码，目录结构可能与下面描述有些出入，后期会慢慢更新修改，感谢大家的关注与支持。

---
*datahub/  数据采集部分*

*fund/ 基金相关的分析部分*

*trader/ 交易部分*

### 文末有券商开户福利：股票万一免5，转债百万之二，还提供券商自动化接口开户
---

码农的量化交易，把经历写成代码推送到github。代码和策略会一直保持更新，如果你有好的策略或者想法和疑问想要交流，可以私信我或者QQ：896820010
### 新增：

### fund

* fund/LOFShareDection.py 监控LOF、ETF场内份额变动
* fund/ark_funds.py 获取ARK ETF每日持仓数据，并写入mongodb
* fund/fund_share_update.py 上交所，深交所 基金场内基金份额监控
* fund/fund_share_monitor.py 上交所，深交所 基金基金份额查询，规模变动
* fund/fund_info_spider.py 集思录基金,腾讯证券基金折价率，溢价率 爬虫
* fund/etf_info.py 市场指数基金的持仓股监控
* fund/ttjj.py 天天基金数据获取



## datahub

* datahub/niwen.py 宁稳可转债下载

* datahub/public_private_fund_members.py 公墓私募基金成员数据

* datahub/jucao_ammouncement.py 巨潮公告批量获取+PDF下载

* datahub/bond_industry_info.py 可转债行业分布

  


### 已有：
* datahub/black_list_sql.py 记录A股市场上所有有黑历史的股票名单，并存入数据库
* big_deal.py 监控每天A股市场上的大单交易
* bond_monitor 可转债监控
* ceiling_break.py 新股一直板开板后多少天能够重新回到开板价格
* delivery_order.py 把交割单导出到Mysql，便于查找某只清仓股的操作历史痕迹，对自己的操作记录一目了然
* fetch_each_day.py --获取每天换手率前50的热门股
* filter_stock.py 通过不同的因子策略选股，常见的如市盈率，流通量，股东数，基金持股数等
* foreign_exchange.py 获取美元汇率的每天走势并存入Mysql
* get_break_high.py --获取当天破50天新高的股票。为什么不获取60天呢？ 因为大家都在用，用的人多了就不准了。 
* ipospeed.py 统计每天IPO新股发行速度与大盘的相关性
* ipo_stock.py 新股统计
* jisilu.py 获取集思录的可转债行情
* jubi.py -获取国内山寨币平台的实时数据
* new_stock_break 分析新股的开板时机
* new_stock_fund 打新基金获取，并选出中签科创板的基金
* pledgeed_validation.py 股权质押数据整理
* push_msn.py -短信提醒自己 设定的某个股票价格或者涨幅达到自己 要求
* relationship_case.py 每个月的解禁股与大盘指数的关系
* select_stock.py - 选股策略， 根据自己的经验选出来的个股。 
* SPSIOP_PRICE.py - 华宝油气估值 通过爬虫获取数据然后计算
* stockInfo.py 爬取市场股票新闻消息，并存储到ElasticSearch数据库中
* strategy_verify.py 获取雪球的策略并验证
* simulation.py 记录自己的模拟仓
* strategy_verify.py -获取雪球的即时交易策略
* win_or_lost_each_day.py --评估自己每天每只股票的盈亏情况 完成度100%
* zdt.py --每天股票市场的涨停热度 

###

# 福利

无论做股票还是套利，还是拖拉机6+1，个人比较推荐的一个券商

股票佣金政策：

<br>

* 券商一：

### 可转债沪市百万分之二，深市十万分之四，绝对市场费率最低
[![可转债费率](http://www.30daydo.com/uploads/article/20210313/401533d69e8b1b6ba47ec63e2d0ab2c0.jpg)](http://www.30daydo.com/uploads/article/20210313/401533d69e8b1b6ba47ec63e2d0ab2c0.jpg)

<br>

* 券商二

  ### 无门槛 万1免5
  ### 开户链接：[万一免五](https://q.eqxiu.com/s/KJnKqG9D?eqrcode=1&share_level=1&from_user=41896b82-ca7e-47c3-8d35-735096d82bc0&from_id=bbb4373e-6&share_time=1613626081290&adpop=1)
  国内费率最低，支持同花顺登录
  如果电脑浏览器无法打开链接，可直接扫描下方二维码开户：
  [![二维码开户](http://www.30daydo.com/uploads/article/20210328/e85a8503df62ccb5e8ad3ca322e0d1ef.PNG
  )](http://www.30daydo.com/uploads/article/20210328/e85a8503df62ccb5e8ad3ca322e0d1ef.PNG
  )
  <br>

当然也有其他主流券商可选，华泰，广发，华宝，招商等等，基本可以涵盖主流券商。


<br>

也有港股打新开户，欢迎来撩，非诚勿扰。注明：开户。
----



[![个人微信号](http://www.30daydo.com/uploads/article/20210329/4c87ea0a4f89548ff3db128076c9eebb.jpg)](http://www.30daydo.com/uploads/article/20210329/4c87ea0a4f89548ff3db128076c9eebb.jpg)



----
关注开发者公众号： 可转债量化分析

----
[![公众号](http://www.30daydo.com/uploads/article/20210329/e42c51f95e6e6b41366ee320c1f01316.jpg)](http://www.30daydo.com/uploads/article/20210329/e42c51f95e6e6b41366ee320c1f01316.jpg)