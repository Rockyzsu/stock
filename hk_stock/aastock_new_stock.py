# -*- coding: utf-8 -*-
# @Time : 2021/6/28 23:15
# @File : aastock_new_stock.py
# @Author : Rocky C@www.30daydo.com


'''
http://www.aastocks.com/sc/stocks/market/ipo/listedipo.aspx?s=3&o=0&page=20
'''

import time
from parsel import Selector
from selenium import webdriver
import sys

sys.path.append('..')
import datetime
from common.BaseService import BaseService
from configure.settings import DBSelector

path = r'C:\OneDrive\Python\selenium\chromedriver.exe'


class AAStockNewStock(BaseService):

    def __init__(self):
        super(AAStockNewStock, self).__init__('../log/aastock.log')
        self.conn = DBSelector().get_mysql_conn('db_stock')
        self.cursor = self.conn.cursor()

    def create_table(self):
        sql = '''CREATE TABLE IF NOT EXISTS `tb_hk_new_stock` (
              `id` int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY ,
              `name` varchar(50) DEFAULT NULL,
              `code` varchar(10) NOT NULL,
              `issue_date` date DEFAULT NULL,
              `each_hand_stock` varchar(50) DEFAULT NULL,
              `share_value_Yi` varchar(50) DEFAULT NULL,
              `margin_price` varchar(50) DEFAULT NULL,
              `price` float(255,4) DEFAULT NULL,
              `over_price_part` varchar(50) DEFAULT NULL,
              `hit_least_num` int(255) DEFAULT NULL,
              `hit_ratio` float(255,4) DEFAULT NULL,
              `current_price` float(255,4) DEFAULT NULL,
              `first_day_raise` float(255,4) DEFAULT NULL,
              `accumulate_raise` float(255,4) DEFAULT NULL,
              `crawltime` DATETIME DEFAULT NULL,
              UNIQUE INDEX code_ix(`code` ASC)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''

        try:
            self.cursor.execute(sql)
        except Exception as e:
            print(e)
            self.conn.rollback()
        else:
            self.conn.commit()

    def fetch(self, page):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        prefs = {'profile.managed_default_content_settings.images': 2}
        options.add_experimental_option('prefs', prefs)
        options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36')
        driver = webdriver.Chrome(executable_path=path,
                                  chrome_options=options)
        driver.implicitly_wait(40)

        url = 'http://www.aastocks.com/sc/stocks/market/ipo/listedipo.aspx?s=3&o=0&page={}'
        for p in range(1, page + 1):
            driver.get(url.format(p))
            time.sleep(5)
            yield driver.page_source

    def convert_float(self, data):
        if data is None:
            print('数据为空')
            return None
        data = data.strip().replace('%', '').replace(',', '')

        try:
            print('解析后')
            print(data)
            data = float(data)

        except Exception as e:
            if data != 'N/A':
                print('解析异常')
                print(data)
            data = None
        return data

    def convert_date(self, data_str):
        try:
            date = datetime.datetime.strptime(data_str, '%Y/%m/%d')
        except Exception as e:
            print(e)
            date = None

        return date

    def convert_hand_int(self, data):
        try:
            data = int(data.strip().replace('手', ''))
        except:
            data = None
        return data

    def parse(self, content):
        response = Selector(text=content)
        ipo_list = response.xpath('//div[@id="IPOListed"]/table/tbody/tr')
        insert_sql = '''insert into `tb_hk_new_stock` (`name`,`code`,`issue_date`,`each_hand_stock`,`share_value_Yi`,`margin_price`,`price`,`over_price_part`,`hit_least_num`,`hit_ratio`,`current_price`,`first_day_raise`,`accumulate_raise`,`crawltime`)
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE `crawltime`=%s'''

        for ipo_item in ipo_list:
            item_list = ipo_item.xpath('.//td')
            if len(item_list) < 2:
                continue
            name = item_list[1].xpath('.//a[1]/text()').extract_first()
            code = item_list[1].xpath('.//a[2]/text()').extract_first()
            issue_date = self.convert_date(item_list[2].xpath('.//text()').extract_first())
            each_hand_stock = item_list[3].xpath('.//text()').extract_first()
            share_value_Yi = item_list[4].xpath('.//text()').extract_first()
            margin_price = item_list[5].xpath('.//text()').extract_first()
            price = self.convert_float(item_list[6].xpath('.//text()').extract_first())
            over_price_part = item_list[7].xpath('.//text()').extract_first()
            hit_least_num = self.convert_hand_int(item_list[8].xpath('.//text()').extract_first())
            hit_ratio = self.convert_float(item_list[9].xpath('.//text()').extract_first())
            current_price = self.convert_float(item_list[10].xpath('.//text()').extract_first())
            first_day_raise = self.convert_float(item_list[11].xpath('.//text()').extract_first())
            accumulate_raise = self.convert_float(item_list[12].xpath('.//text()').extract_first())
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            if margin_price == 'N/A':
                # 上市失败的
                continue
            try:
                self.cursor.execute(insert_sql, (
                    name, code, issue_date, each_hand_stock, share_value_Yi, margin_price, price, over_price_part,
                    hit_least_num, hit_ratio, current_price, first_day_raise, accumulate_raise, now, now))
            except Exception as e:
                print(e)
                self.conn.rollback()
            else:
                self.conn.commit()

    def run(self):
        total_page = 25
        self.create_table()
        gen = self.fetch(total_page)
        page = 0
        for content in gen:
            print('page ', page)
            self.parse(content)
            page += 1
        self.conn.close()

    def clear_data(self):
        'select code from tb_hk_new_stock group by code having count(*) as n >1'
        pass


def main():
    app = AAStockNewStock()
    app.run()


if __name__ == '__main__':
    main()
