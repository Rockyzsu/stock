### 更好的帮助自己炒股(亏钱-。-)

#### 2022-12-08 更新

目前正在重构项目代码，目录结构可能与下面描述有些出入，后期会慢慢更新修改，感谢大家的关注与支持。

---

*analysis/ 数据分析部分*

*datahub/ 数据采集部分*

*fund/ 基金相关的分析部分*

*futu/ 富途牛牛接口的基本用法 *

*hk_stock/ 港股部分*

*k-line/ K线技术形态部分*

*machine_learning/ 机器学习预测* 

*trader/ 交易部分*

*ptrade/ ptrade自动交易实盘代码*

*log/* 存放日志

*common/* 常用函数与库

*configure* 数据库连接与配置

----
#### 使用教程：
* 修改 configure/sample_config.json 配置文件名 为 configure/config.json，根据不同项目，并对着里面的字段进行修改，修改你的mysql，mongodb的用户名和密码，如果项目里面没有用到mysql，mongodb等，则不需要修改。
对应的映射关系可以看这个文件里面的源码。这个设置主要为了同一套代码便于切换线上和本地的数据库，并没有采用环境变量的方式存储用户密码。需要的朋友也可以自己改动。

configure/setting.py

```
    def config(self, db_type='mysql', local='ubuntu'):
        db_dict = self.json_data[db_type][local]
        user = db_dict['user']
        password = db_dict['password']
        host = db_dict['host']
        port = db_dict['port']
        return (user, password, host, port)

    def get_engine(self, db, type_='ubuntu'):
        from sqlalchemy import create_engine
        user, password, host, port = self.config(db_type='mysql', local=type_)
        try:
            engine = create_engine(
                'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(user, password, host, port, db))
        except Exception as e:
            print(e)
            return None
        return engine

    def get_mysql_conn(self, db, type_='ubuntu'):
        import pymysql
        user, password, host, port = self.config(db_type='mysql', local=type_)
        try:
            conn = pymysql.connect(host=host, port=port, user=user, password=password, db=db, charset='utf8')
        except Exception as e:
            print(e)
            return None
        else:
            return conn

    def mongo(self, location_type='ubuntu', async_type=False):
        user, password, host, port = self.config('mongo', location_type)
        connect_uri = f'mongodb://{user}:{password}@{host}:{port}'
        if async_type:
            from motor.motor_asyncio import AsyncIOMotorClient
            client = AsyncIOMotorClient(connect_uri)
        else:
            import pymongo
            client = pymongo.MongoClient(connect_uri)
        return client
```

#### 文末有券商福利：提供券商自动化下单接口

---

码农的量化交易，把经历写成代码推送到github。代码和策略会一直保持更新，如果你有好的策略或者想法和疑问想要交流，可以加文末微信。

### 新增：

### analysis 目录 数据分析部分

* analysis/get_zt_info 分析次新板块中的涨停强度
* analysis/diagnose_stock 股票诊断，是否有黑历史和东北股
* analysis/ipospeed IPO发行速度 与指数的相关性
* analysis/fd_money A股某段日期内涨停板的封单金额 
* 
### fund（基金）

* fund/LOFShareDection.py 监控LOF、ETF场内份额变动
* fund/ark_funds.py 获取ARK ETF每日持仓数据，并写入mongodb
* fund/fund_share_update.py 上交所，深交所 基金场内基金份额监控
* fund/fund_share_monitor.py 上交所，深交所 基金基金份额查询，规模变动
* fund/fund_info_spider.py 集思录基金,腾讯证券基金折价率，溢价率 爬虫
* fund/etf_info.py 市场指数基金的持仓股监控
* fund/ttjj.py 天天基金数据获取
* fund/xueqiu_private_fund.py 雪球私募私募获取
* fund/danjuan_fund.py 雪球蛋卷基金数据获取
* fund/danjuan_fund_data_analysis.py 雪球蛋卷基金分析

## datahub（数据源）

* datahub/foreignexchange.py 美元兑人民币汇率监控
* datahub/niwen.py 宁稳可转债下载
* datahub/public_private_fund_members.py 公墓私募基金成员数据
* datahub/jucao_ammouncement.py 巨潮公告批量获取+PDF下载
* datahub/bond_industry_info.py 可转债行业分布
* datahub/ceiling_break.py 涨停板封榜监控

## k-line （K线技术形态识别）
* k-line/recognize_form.py 通过talib识别常见形态，如三只乌鸦等
* 
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

----

# 福利

### 券商量化下单接口

支持python语言，可云端部署与本地运行两种模式，支持A股市场股票，转债，基金等品种。

![实盘python下单接口](http://xximg.30daydo.com/picgo/ptrade1.png)

### 接口文档

![](http://xximg.30daydo.com/picgo/api%E6%96%87%E6%A1%A3.png)

### 费率

交易费率低：<br>
股票万一； 可转债万0.4；基金ETF,LOF万0.5


----

开通量化接口后是不收取额外费用，可永久使用。

开通条件：
不同券商门槛不同
* 券商一：开户后入金1W可开通
* 券商二：开户后入金2W即可开通
* 

----

当然也有其他主流券商可选，华泰，广发，华宝，招商，国金，银河证券等等，基本可以涵盖主流券商。

----

## 开通方式：

扫码


<img src="http://xximg.30daydo.com/picgo/ufc200.png" style="zoom:80%;" />
<br>注明：开户。


----
关注开发者公众号： 可转债量化分析

----

[![公众号](http://www.30daydo.com/uploads/article/20210329/e42c51f95e6e6b41366ee320c1f01316.jpg)](http://www.30daydo.com/uploads/article/20210329/e42c51f95e6e6b41366ee320c1f01316.jpg)