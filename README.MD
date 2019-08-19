### 更好的帮助自己炒股(亏钱-。-)
本人业余投机者（韭菜）一枚，自学量化交易，把经历写成代码推送到github。代码和策略会一直保持更新，如果你有好的策略或者想法和疑问想要交流，可以私信我或者QQ：896820010

* black_list_sql.py 记录A股市场上所有有黑历史的股票名单，并存入数据库
* big_deal.py 监控每天A股市场上的大单交易
* bond_monitor 可转债监控
* ceiling_break.py 新股一直板开板后多少天能够重新回到开板价格
* delivery_order.py 把交割单导出到Mysql，便于查找某只清仓股的操作历史痕迹，对自己的操作记录一目了然
* fetch_each_day.py --获取每天换手率前50的热门股
* filter_stock.py 通过不同的因子策略选股，常见的如市盈率，流通量，股东数，基金持股数等
* foreign_exchange.py 获取美元汇率的每天走势并存入Mysql
* get_break_high.py --获取当天破50天新高的股票。为什么不获取60天呢？ 因为大家都在用，用的人多了就不准了。 
* ipo_speed.py 统计每天IPO新股发行速度与大盘的相关性
* ipo_stock.py 新股统计
* jisilu.py 获取集思录的可转债行情
* jubi.py -获取国内山寨币平台的实时数据
* new_stock_break 分析新股的开板时机
* pledgeed_validation.py 股权质押数据整理
* push_msn.py -短信提醒自己 设定的某个股票价格或者涨幅达到自己 要求
* relationship_case.py 每个月的解禁股与大盘指数的关系
* select_stock.py - 选股策略， 根据自己的经验选出来的个股。 
* stockInfo.py 爬取市场股票新闻消息，并存储到ElasticSearch数据库中
* strategy_verify.py 获取雪球的策略并验证
* simulation.py 记录自己的模拟仓
* strategy_verify.py -获取雪球的即时交易策略
* win_or_lost_each_day.py --评估自己每天每只股票的盈亏情况 完成度100%
* zdt.py --每天股票市场的涨停热度 

###
您的支持就是我最大的动力！
如果您觉得本示例对你有用，作为对作者的打赏，可以扫描以下支付宝红包,这是作者的免费红包二维码，领取了到店铺支付时使用，可抵扣相应金额。

![alipay](resource/redbag.jpg )

如果您真的很感激作者，也可以直接扫描以下二维码打赏作者。

![weixin](resource/weixin.png)    
![alipay](resource/MyAlipay.jpg)  