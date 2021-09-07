# -*-coding=utf-8-*-
import os, re
import pymysql
import setting

db_name = 'db_news'
conn = pymysql.connect(host=setting.MYSQL_REMOTE,
                       port=3306,
                       user=setting.MYSQL_REMOTE_USER,
                       passwd=setting.MYSQL_PASSWORD,
                       db=db_name,
                       charset='utf8'
                       )

cur = conn.cursor()


def create_tb():
    cmd = '''CREATE TABLE IF NOT EXISTS tb_cnstock(Date DATETIME ,Title VARCHAR (80),URL VARCHAR (80),PRIMARY KEY (URL)) charset=utf8;'''
    try:
        cur.execute(cmd)
        conn.commit()
        # conn.close()
        return True
    except Exception as e:
        print(e)
        conn.rollback()
        return False


def save_sql():
    if not create_tb():
        return False

    files = os.listdir('.')
    for file in files:
        years = re.findall(r'StockNews-\[(.*?)\]-\[.*?\].log', file)
        if len(years):
            print(file)
            cur_year = years[0].split('-')[0]
            f = open(file).readlines()
            loop=4
            count=1
            for content in f:
                s = content.strip()
                # print(s)

                if count%loop==2:
                    # if re.search(r'\d+-\d+ \d+:\d+', s):
                    # print(s.split()[2])
                    # pass
                    date_times = re.findall('(\d+-\d+ \d+:\d+)', s)[0]
                    date_times=cur_year+'-'+date_times

                    titles = re.findall(r'\d+-\d+ \d+:\d+(.*)', s)[0]  # 03-06 16:53
                    titles=titles.strip()

                    # print(title)
                    # if title:
                    #     titles = title[0]
                    #     print('title', titles)
                    # if date_time:
                    #     date_times = date_time[0]
                    #     print('date:', date_times)

                # print('new line')
                if count%loop==3:
                # if re.search(r'--->', s):
                #     print(s)
                    # pass
                    url_link = re.findall(r'---> (.*)', s)[0]
                    # if url_link:
                    #     print('stock_url', url_link[0])
                # date_times='h'
                # titles='h'
                # url_link='h'
                if (count%loop==0) and (date_times) and (titles) and (url_link):
                    cmd='''INSERT INTO tb_cnstock (Date,Title,URL ) VALUES(\'%s\',\'%s\',\'%s\');''' % (date_times, titles, url_link)
                    print(cmd)
                    try:
                        cur.execute(cmd)
                        conn.commit()
                    except Exception as e:
                        print(e)
                        conn.rollback()
                count=count+1

    conn.close()
    return True


if __name__ == "__main__":

    # sub_folder = os.path.join(os.path.dirname(__file__), "data")
    sub_folder=r'C:\OneDrive\Python\all_in_one\data'
    if not os.path.exists(sub_folder):
        os.mkdir(sub_folder)
    os.chdir(sub_folder)
    save_sql()
