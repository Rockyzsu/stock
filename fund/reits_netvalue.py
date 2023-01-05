# 获取REITS净值
import datetime
import requests
import sys
import re

sys.path.append('..')
from configure.util import jsonp2json, send_message_via_wechat
from configure.settings import DBSelector

use_xq = True  # 数据源


class ReitsNetValue:

    def __init__(self):
        self.today = datetime.datetime.now().strftime('%Y-%m-%d')
        self.conn = DBSelector().get_mysql_conn('db_reits', 'tencent-1c')
        self.init_db()

    def parse(self, js, code):
        history_netvalue = js.get('Data').get('LSJZList')
        if history_netvalue is None:
            send_message_via_wechat('{}净值为空'.format(code))
            return

        for v in history_netvalue:
            value = v.get('DWJZ')  # 单位净值
            value = float(value)
            # 只取一个
            return value

    def _crawl(self, code):

        cookies = {
            'qgqp_b_id': '332e88303d7106e94890d3f5092fefe0',
            'em_hq_fls': 'js',
            'em-quote-version': 'topspeed',
            'AUTH_FUND.EASTMONEY.COM_GSJZ': 'AUTH*TTJJ*TOKEN',
            'mtp': '1',
            'sid': '122139003',
            'vtpst': '|',
            'ct': 'j1dOTKvx0n34erwykWJT-LkDgtdqlgpIKqhaHBuGQoVYs-5dMUpIvnSlPVAXyHn4fqWREcXeNAsmo50J5F84BlVtjsHslZipCIVHjhGT1hUIH0F08toeazXUD3-sc0kjkjWruaRlT80EiY-WGnjbS_kRAk-68Aht9mATkPn2V7w',
            'ut': 'FobyicMgeV52Ad4fCxim_J6Hiu_4oWVEmHIb_3mK_yBtSzU4NYwbb1XsCEwlNgravTA1WEhUxX_plWYgcyvv6uREyRhSEJuEk97vKkA83wkmUHbFQ5IH-6Q8zf0BJRewneTV1hKCWAkQ-bvJwMFO7btMLv0YgycBzupPDDp5bqEOOMxP3i_DMBHVmI1xPqxHRiyLqep9LNlZu9WrFc_KKG6gSKmTzs9-eEDRQ0JKMRVyqSxwRgsVJCurEHqL2hM6E7q-GPjcqA-Q6h5Re2GNkmQfnW5cLygQ',
            'pi': '6590645210394316%3bk6590645210394316%3b%e5%8f%af%e8%bd%ac%e5%80%ba%e9%87%8f%e5%8c%96%e5%88%86%e6%9e%90%3bs5KvmCIggz%2byOz%2fkj9QXhelbHbq4%2fBnASP5ql16GcFwxOUB8j%2fYmyJpy0HxykvZMKc5LL0tbIPYL8FHmCEIjY%2b0j%2bWIh3o8AGcg6kfGdJGERRU1dSm9fAaO4aEeHqJC8gXGDXkMaREsjWIZhbT9%2fa8mP5d0klCVoQtE0IBoAM0tQR%2bqtK8ot5FKkxw%2bnHSfjSrYdRm%2ft%3bCknGIwcEf88zLcToJmOXWQLq3GYVRzB%2bCVwDf2BaM4K%2bYW1mbDF5PmMJFwER7bwAmz%2buYfOkCRn4I17Nx4d%2fowe0ifes6eR8JbieW0X2zFpqLgn3jQ%2feaRn6R3ifly8t9Sc%2fa7lgoFlFV5JCtjI3f0u5Zzus9A%3d%3d',
            'uidal': '6590645210394316%e5%8f%af%e8%bd%ac%e5%80%ba%e9%87%8f%e5%8c%96%e5%88%86%e6%9e%90',
            'isCoverBgSelectCrop': 'true',
            'EmFundFavorVersion2': '0',
            'st_si': '64325209590844',
            'st_asi': 'delete',
            'HAList': 'ty-1-508099-%u5EFA%u4FE1%u4E2D%u5173%u6751REIT%2Cty-0-180501-%u7EA2%u571F%u6DF1%u5733%u5B89%u5C45REIT%2Cty-90-BK0528-%u8F6C%u503A%u6807%u7684%2Ca-sh-124290-PR%u957F%u8F68%u4EA4%2Cty-1-508066-%u82CF%u4EA4REIT%2Cty-1-508009-%u5B89%u5FBD%u4EA4%u63A7%2Cty-1-508018-%u534E%u590F%u4E2D%u56FD%u4EA4%u5EFAREIT%2Cty-0-180801-%u4E2D%u822A%u9996%u94A2%u7EFF%u80FDREIT%2Cty-0-300498-%u6E29%u6C0F%u80A1%u4EFD%2Cty-1-600754-%u9526%u6C5F%u9152%u5E97',
            'guba_blackUserList': '2546376295120552',
            'st_pvi': '30849193689390',
            'st_sp': '2022-02-19%2022%3A30%3A59',
            'st_inirUrl': 'https%3A%2F%2Ffund.eastmoney.com%2F',
            'st_sn': '11',
            'st_psi': '20230105113427388-113200301327-1659036638',
        }

        headers = {
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
            'sec-ch-ua-mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'sec-ch-ua-platform': '"Linux"',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Dest': 'script',
            'Referer': 'https://fundf10.eastmoney.com/',
            'Accept-Language': 'zh,en;q=0.9,en-US;q=0.8,zh-CN;q=0.7,zh-TW;q=0.6',
            # 'Cookie': 'qgqp_b_id=332e88303d7106e94890d3f5092fefe0; em_hq_fls=js; em-quote-version=topspeed; AUTH_FUND.EASTMONEY.COM_GSJZ=AUTH*TTJJ*TOKEN; mtp=1; sid=122139003; vtpst=|; ct=j1dOTKvx0n34erwykWJT-LkDgtdqlgpIKqhaHBuGQoVYs-5dMUpIvnSlPVAXyHn4fqWREcXeNAsmo50J5F84BlVtjsHslZipCIVHjhGT1hUIH0F08toeazXUD3-sc0kjkjWruaRlT80EiY-WGnjbS_kRAk-68Aht9mATkPn2V7w; ut=FobyicMgeV52Ad4fCxim_J6Hiu_4oWVEmHIb_3mK_yBtSzU4NYwbb1XsCEwlNgravTA1WEhUxX_plWYgcyvv6uREyRhSEJuEk97vKkA83wkmUHbFQ5IH-6Q8zf0BJRewneTV1hKCWAkQ-bvJwMFO7btMLv0YgycBzupPDDp5bqEOOMxP3i_DMBHVmI1xPqxHRiyLqep9LNlZu9WrFc_KKG6gSKmTzs9-eEDRQ0JKMRVyqSxwRgsVJCurEHqL2hM6E7q-GPjcqA-Q6h5Re2GNkmQfnW5cLygQ; pi=6590645210394316%3bk6590645210394316%3b%e5%8f%af%e8%bd%ac%e5%80%ba%e9%87%8f%e5%8c%96%e5%88%86%e6%9e%90%3bs5KvmCIggz%2byOz%2fkj9QXhelbHbq4%2fBnASP5ql16GcFwxOUB8j%2fYmyJpy0HxykvZMKc5LL0tbIPYL8FHmCEIjY%2b0j%2bWIh3o8AGcg6kfGdJGERRU1dSm9fAaO4aEeHqJC8gXGDXkMaREsjWIZhbT9%2fa8mP5d0klCVoQtE0IBoAM0tQR%2bqtK8ot5FKkxw%2bnHSfjSrYdRm%2ft%3bCknGIwcEf88zLcToJmOXWQLq3GYVRzB%2bCVwDf2BaM4K%2bYW1mbDF5PmMJFwER7bwAmz%2buYfOkCRn4I17Nx4d%2fowe0ifes6eR8JbieW0X2zFpqLgn3jQ%2feaRn6R3ifly8t9Sc%2fa7lgoFlFV5JCtjI3f0u5Zzus9A%3d%3d; uidal=6590645210394316%e5%8f%af%e8%bd%ac%e5%80%ba%e9%87%8f%e5%8c%96%e5%88%86%e6%9e%90; isCoverBgSelectCrop=true; EmFundFavorVersion2=0; st_si=64325209590844; st_asi=delete; HAList=ty-1-508099-%u5EFA%u4FE1%u4E2D%u5173%u6751REIT%2Cty-0-180501-%u7EA2%u571F%u6DF1%u5733%u5B89%u5C45REIT%2Cty-90-BK0528-%u8F6C%u503A%u6807%u7684%2Ca-sh-124290-PR%u957F%u8F68%u4EA4%2Cty-1-508066-%u82CF%u4EA4REIT%2Cty-1-508009-%u5B89%u5FBD%u4EA4%u63A7%2Cty-1-508018-%u534E%u590F%u4E2D%u56FD%u4EA4%u5EFAREIT%2Cty-0-180801-%u4E2D%u822A%u9996%u94A2%u7EFF%u80FDREIT%2Cty-0-300498-%u6E29%u6C0F%u80A1%u4EFD%2Cty-1-600754-%u9526%u6C5F%u9152%u5E97; guba_blackUserList=2546376295120552; st_pvi=30849193689390; st_sp=2022-02-19%2022%3A30%3A59; st_inirUrl=https%3A%2F%2Ffund.eastmoney.com%2F; st_sn=11; st_psi=20230105113427388-113200301327-1659036638',
        }

        params = {
            'callback': 'jQuery1830021091296784611746_1672888084129',
            'fundCode': code,
            'pageIndex': '1',
            'pageSize': '20',
            'startDate': '',
            'endDate': '',
            '_': '1672889709799',
        }

        response = requests.get('https://api.fund.eastmoney.com/f10/lsjz', params=params, cookies=cookies,
                                headers=headers)
        # print(response.text)
        return response.text

    def _crawl_xueqiu(self, code):

        cookies = {
            'device_id': 'a17524517d64d99ddef6e4461172f193',
            's': 'bm121wffjs',
            'bid': '4a7809eff12dfb426fecf9028b9a8727_l4uxvrvc',
            '__utmz': '1.1656225474.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
            'Hm_lvt_fe218c11eab60b6ab1b6f84fb38bcc4a': '1665024572',
            '__utma': '1.1419494795.1656225474.1664588616.1666267539.5',
            'acw_tc': '2760826416729018198398134e73095176de6c11cfdc2253bd48f682437a5a',
            'xq_a_token': '140b9d69cb9f100ad486013ceeb783e9bb0696f5',
            'xqat': '140b9d69cb9f100ad486013ceeb783e9bb0696f5',
            'xq_r_token': '51944912a96da76eef33a19d179cbfa8812d17e8',
            'xq_id_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTY3NDc3ODgwNiwiY3RtIjoxNjcyOTAxNzg3NjM3LCJjaWQiOiJkOWQwbjRBWnVwIn0.Kxgsb_pvhnfJi_TYN7kZMPNa6coextiPeuuoJxw59h7JHVIW9SgxeCreaB3RVEb0lXhJN7F38J19fovrDCm7pLYKGQZIVKtwaRdpoxc25jveiLtX8Mv4wKCPiaSYe4Fn1uUHIUUogbfcWKS1-TNO5d9d_Bp-qISwUfzITJfk6z3jgiiO6v4pEtXpI1URCYpp0fBFHSh4zdF9gPYUL2_tt2rM6z4x9shdisFhC0pcMyOllrMY-UnpqEYXo1arfh4SuPvQjFTM0PF2-fviOXWQTicuFHuVVreThAtsklEki0qu1Hzo2NDmlF3TxT1oCZkRVDSwigweB-EYxSnQjRT0Cw',
            'u': '741672901819844',
            'is_overseas': '0',
            'Hm_lvt_1db88642e346389874251b5a1eded6e3': '1670512071,1670995961,1672799893,1672901824',
            'Hm_lpvt_1db88642e346389874251b5a1eded6e3': '1672901824',
        }

        headers = {
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            # 'Cookie': 'device_id=a17524517d64d99ddef6e4461172f193; s=bm121wffjs; bid=4a7809eff12dfb426fecf9028b9a8727_l4uxvrvc; __utmz=1.1656225474.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); Hm_lvt_fe218c11eab60b6ab1b6f84fb38bcc4a=1665024572; __utma=1.1419494795.1656225474.1664588616.1666267539.5; acw_tc=2760826416729018198398134e73095176de6c11cfdc2253bd48f682437a5a; xq_a_token=140b9d69cb9f100ad486013ceeb783e9bb0696f5; xqat=140b9d69cb9f100ad486013ceeb783e9bb0696f5; xq_r_token=51944912a96da76eef33a19d179cbfa8812d17e8; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTY3NDc3ODgwNiwiY3RtIjoxNjcyOTAxNzg3NjM3LCJjaWQiOiJkOWQwbjRBWnVwIn0.Kxgsb_pvhnfJi_TYN7kZMPNa6coextiPeuuoJxw59h7JHVIW9SgxeCreaB3RVEb0lXhJN7F38J19fovrDCm7pLYKGQZIVKtwaRdpoxc25jveiLtX8Mv4wKCPiaSYe4Fn1uUHIUUogbfcWKS1-TNO5d9d_Bp-qISwUfzITJfk6z3jgiiO6v4pEtXpI1URCYpp0fBFHSh4zdF9gPYUL2_tt2rM6z4x9shdisFhC0pcMyOllrMY-UnpqEYXo1arfh4SuPvQjFTM0PF2-fviOXWQTicuFHuVVreThAtsklEki0qu1Hzo2NDmlF3TxT1oCZkRVDSwigweB-EYxSnQjRT0Cw; u=741672901819844; is_overseas=0; Hm_lvt_1db88642e346389874251b5a1eded6e3=1670512071,1670995961,1672799893,1672901824; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1672901824',
        }
        if code.startswith('5'):
            code = 'SH' + code
        else:
            code = 'SZ' + code

        response = requests.get('https://xueqiu.com/S/{}'.format(code), cookies=cookies, headers=headers)
        return response.text

    def update_sql(self, sql_str, data):
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql_str, args=data)
        except Exception as e:
            send_message_via_wechat('更新数据错误 {}'.format(e))
            self.conn.rollback()
        else:
            self.conn.commit()

    def dump_mysql(self, code, name, netvalue, updated):
        sql_str = 'insert into `tb-reits-netvalue` (code,name,netvalue,updated) values (%s,%s,%s,%s) on duplicate key update `netvalue`=%s,updated=%s'
        self.update_sql(sql_str, (code, name, netvalue, updated, netvalue,updated))

    def parse_xueqiu(self, content):

        m = re.search('"acc_unit_nav":(.*?),', content)
        if m:
            return float(m.group(1))
        return 0

    def get_netvalue_by_code(self, code, name):
        if use_xq:
            text = self._crawl_xueqiu(code)
            netvalue = self.parse_xueqiu(text)
        else:
            text = self._crawl(code)
            js = jsonp2json(text)
            netvalue = self.parse(js,code)

        updated_time = datetime.datetime.now()
        self.dump_mysql(code, name, netvalue, updated_time)

    def read_sql(self, sql_str, data):
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql_str, data)
        except Exception as e:
            send_message_via_wechat('{}'.format(e))
            raise ValueError(e)
        else:
            result = cursor.fetchall()
        return result

    def get_all_codes(self):
        sql_str = 'select `代码`,`名称` from `reits-{}` where `最新价`<>%s'.format('2023-01-04')
        result = self.read_sql(sql_str, ('-',))
        code_list = []
        for item in result:
            code_list.append((item[0], item[1]))
        return code_list

    def init_db(self):
        sql_str = 'create table if not exists `tb-reits-netvalue` (code varchar(6) ,name varchar(128),netvalue float,updated datetime,primary key(code)) engine=InnoDB default charset=utf8mb4'
        self.update_sql(sql_str, None)

    def run(self):
        all_reits_code = self.get_all_codes()
        for code, name in all_reits_code:
            self.get_netvalue_by_code(code, name)


if __name__ == '__main__':
    app = ReitsNetValue()
    app.run()
