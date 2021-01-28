# -*- coding: UTF-8 -*-
"""
@author:xda
@file:sz_etf.py
@time:2021/01/24
"""

# 后续废弃


def szse_etf():
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    sess = requests.Session()
    url = 'http://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1812_zs&TABKEY=tab1&PAGENO={}&random=0.4572618756063547'
    for i in range(1, 10):
        s = sess.get(url=url.format(i), headers={'User-Agent': 'Molliza Firefox Chrome'})
        ret = s.json()
        if len(ret) > 0:
            data = ret[0].get('data')
            for d in data:
                zsdm = d.get('zsdm')
                zsmc = d.get('zsmc')

                code = re.search('<u>(.*?)</u>', zsdm).group(1)
                detail_url = re.search('href=\'(.*?)\'', zsdm).group(1)
                name = re.search('<u>(.*?)</u>', zsmc).group(1)

                jrnew = d.get('jrnew')
                jrzs = d.get('jrzs')
                qsrnew = d.get('qsrnew')

                obj = IndexObjectSZ(
                    代码=code,
                    指数名称=name,
                    详细URL=detail_url,

                    基日=jrnew,
                    基日指数=jrzs,
                    起始计算日=qsrnew,
                )

                session.add(obj)
                session.commit()


def szse_etf_detail():
    client = pymongo.MongoClient()
    doc = client['fund']['etf_info_sz']

    Session = sessionmaker(bind=engine)
    session = Session()
    ret = session.query(IndexObjectSZ).all()
    sess = requests.Session()
    url = 'http://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1747_zs&TABKEY=tab1&ZSDM={}&random=0.5790989240667317'

    sub_url = 'http://www.szse.cn/api/report/ShowReport/data?SHOWTYPE=JSON&CATALOGID=1747_zs&TABKEY=tab1&PAGENO={}&ZSDM={}&random=0.29981446895718666'
    for item in ret:
        code = item.代码
        name = item.指数名称
        r = sess.get(url.format(code), headers={'User-Agent': 'Molliza Firefox Chrome'})
        js = r.json()
        t = {}
        t['指数代码'] = code
        t['指数名称'] = name
        t_list = []

        if js is not None and len(js) > 0:
            data = js[0]
            page = data.get('metadata', {}).get('pagecount', 0)
            for i in range(1, page + 1):
                s1 = sess.get(url=sub_url.format(i, code), headers={'User-Agent': 'Molliza Firefox Chrome'})
                r1 = s1.json()
                if r1 is not None and len(r1) > 0:
                    stock_list = r1[0].get('data')
                    for st in stock_list:
                        zqdm = st.get('zqdm')
                        zqjc = st.get('zqjc')
                        zgb = st.get('zgb')  # 总股本
                        ltgb = st.get('ltgb')  # 流通股本
                        hylb = st.get('hylb')  #
                        nrzsjs = st.get('nrzsjs')
                        d = {}
                        d['证券代码'] = zqdm
                        d['证券简称'] = zqjc
                        d['总股本'] = zgb
                        d['流通股本'] = ltgb
                        d['行业列表'] = hylb
                        d['nrzsjs'] = nrzsjs
                        t_list.append(d)
        t['成分股数据'] = t_list

        try:
            doc.insert_one(t)
        except Exception as e:
            logger.error(e)

