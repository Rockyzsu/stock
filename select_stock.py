# -*-coding=utf-8-*-
# 适用 tushare 0.7.5
__author__ = 'Rocky'
import tushare as ts
import pandas as pd
import os, sys, datetime, time,Queue
import numpy as np
from toolkit import Toolkit
from threading import Thread
q=Queue.Queue()
reload(sys)
sys.setdefaultencoding('utf-8')
# 用来选股用的
# pd.set_option('max_rows',None)
# 缺陷： 暂时不能保存为excel
class select_class():
    def __init__(self):
        #self.bases=ts.get_stock_basics()

        #self.bases.to_csv('bases.csv')

        # 因为网速问题，手动从本地抓取
        self.today = time.strftime("%Y-%m-%d", time.localtime())
        self.base = pd.read_csv('bases.csv', dtype={'code': np.str})
        self.all_code = self.base['code'].values
        self.working_count=0
        self.mystocklist = Toolkit.read_stock('mystock.csv')

    # 保存为excel 文件 这个时候csv 乱码,excel正常.
    def save_data_excel(self):
        df = ts.get_stock_basics()

        df.to_csv(self.today + '.csv', encoding='gbk')
        df_x = pd.read_csv(self.today + '.csv', encoding='gbk')
        df_x.to_excel(self.today + '.xls', encoding='gbk')
        os.remove(self.today + '.csv')

    def insert_garbe(self):
        print '*' * 30
        print '\n'

    def showInfo(self, df):
        print '*' * 30
        print '\n'
        print df.info()
        print '*' * 30
        print '\n'
        print df.dtypes
        self.insert_garbe()
        print df.describe()

    # 计算每个地区有多少上市公司
    def count_area(self, writeable=False):
        count = self.base['area'].value_counts()
        print count
        print type(count)
        if writeable:
            count.to_csv(u'各省的上市公司数目.csv')
        return count

    # 显示你要的某个省的上市公司
    def get_area(self, area, writeable=False):
        user_area = self.base[self.base['area'] == area]
        user_area.sort_values('timeToMarket', inplace=True, ascending=False)
        if writeable:
            filename = area + '.csv'
            user_area.to_csv(filename)
        return user_area


    # 获取所有地区的分类个股
    def get_all_location(self):
        series = self.count_area()
        index = series.index
        for i in index:
            name = unicode(i)
            self.get_area(name, writeable=True)

    # 找出指定日期后的次新股
    def fetch_new_ipo(self, start_time, writeable=False):
        # 需要继续转化为日期类型

        df = self.base.loc[self.base['timeToMarket'] > start_time]
        df.sort_values('timeToMarket', inplace=True, ascending=False)
        if writeable == True:
            df.to_csv("New_IPO.csv")
        #sum_a=df['pe'].sum()

        pe_av=df[df['pe']!=0]['pe'].mean()
        pe_all_av=self.base[self.base['pe']!=0]['pe'].mean()
        print u"平均市盈率为 " , pe_av
        print u'A股的平均市盈率为 ',pe_all_av
        return df


    #获取成分股
    def get_chengfenggu(self,writeable=False):
        s50=ts.get_sz50s()
        if writeable==True:
            s50.to_excel('sz50.xls')
        list_s50=s50['code'].values.tolist()
        #print type(s50)
        #print type(list_s50)
        #返回list类型
        return list_s50
    # 计算一个票从最高位到目前 下跌多少 计算跌幅
    def drop_down_from_high(self, start, code):

        end_day = datetime.date(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day)
        end_day = end_day.strftime("%Y-%m-%d")
        # print end_day
        # print start
        total = ts.get_k_data(code=code, start=start, end=end_day)
        # print total
        high = total['high'].max()
        high_day = total.loc[total['high'] == high]['date'].values[0]

        print high
        print high_day
        current = total['close'].values[-1]
        print current
        percent = round((current - high) / high * 100, 2)
        print percent
        return percent

    def loop_each_cixin(self):
        df = self.fetch_new_ipo(20170101,writeable=False)
        all_code = df['code'].values
        print all_code
        # exit()
        percents = []
        for each in all_code:
            print each
            # print type(each)
            percent = self.drop_down_from_high('2017-01-01', each)
            percents.append(percent)

        df['Drop_Down'] = percents

        #print df

        df.sort_values('Drop_Down', ascending=True, inplace=True)
        #print df
        df.to_csv(self.today+'_drop_Down_cixin.csv')



    # 获取所有的ma5>ma10
    def macd(self):
        # df=self.fetch_new_ipo(writeable=True)
        # all_code=df['code'].values
        # all_code=self.get_all_code()
        # print all_code
        result = []
        for each_code in self.all_code:
            print each_code
            try:
                df_x = ts.get_k_data(code=each_code, start='2017-03-01')
            # 只找最近一个月的，所以no item的是停牌。
            except:
                print "Can't get k_data"
                continue
            if len(df_x) < 11:
                # return
                print "no item"
                continue
            ma5 = df_x['close'][-5:].mean()
            ma10 = df_x['close'][-10:].mean()
            if ma5 > ma10:
                # print "m5>m10: ",each_code," ",self.base[self.base['code']==each_code]['name'].values[0], "ma5: ",ma5,' m10: ',ma10
                temp = [each_code, self.base[self.base['code'] == each_code]['name'].values[0]]
                print temp
                result.append(temp)
        print result
        print "Done"
        return result

    def get_all_code(self):
        return self.all_code

    # 获取成交量的ma5 或者10
    def volume_calculate(self,codes):
        delta_day = 180 * 7 / 5
        end_day = datetime.date(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day)
        start_day = end_day - datetime.timedelta(delta_day)

        start_day = start_day.strftime("%Y-%m-%d")
        end_day = end_day.strftime("%Y-%m-%d")
        print start_day
        print end_day
        result=[]
        for each_code in codes:
            # print each_code
            try:
                df = ts.get_k_data(each_code, start=start_day, end=end_day)

            except:
                print "Failed to get"
                continue
            # print df
            all_mean = df['volume'].mean()
            if len(df) < 11:
                # print "not long enough"
                continue
            m5_volume_m = df['volume'][-5:].mean()
            m10_volume_m = df['volume'][-10:].mean()

            #在这里分几个分支，放量 180天均量的4倍
            if  m5_volume_m > (4.0 * all_mean):
                print "m5 > m_all_avg "
                print each_code,
                temp = self.base[self.base['code'] == each_code]['name'].values[0]
                print temp
                result.append(each_code)
        return result

    def turnover_check(self):
        delta_day = 60 * 7 / 5
        end_day = datetime.date(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day)
        start_day = end_day - datetime.timedelta(delta_day)

        start_day = start_day.strftime("%Y-%m-%d")
        end_day = end_day.strftime("%Y-%m-%d")
        print start_day
        print end_day
        for each_code in self.all_code:
            try:
                df = ts.get_hist_data(code=each_code, start=start_day, end=end_day)
            except:
                print "Failed to get data"
                continue
            mv5 = df['v_ma5'][-1]
            mv20 = df['v_ma20'][-1]
            mv_all = df['volume'].mean()
            print

    # 写入csv文件
    def write_to_text(self):
        print "On write"
        r = self.macd()
        filename = self.today + "-macd.csv"
        f = open(filename, 'w')
        for i in r:
            f.write(i[0])
            f.write(',')
            f.write(i[1])
            f.write('\n')
        f.close()

    # 读取自己的csv文件
    def read_csv(self):
        filename = self.today + "-macd.csv"
        df = pd.read_csv(filename)
        print df

    # 持股从高点下跌幅度
    def own_drop_down(self):
        for i in self.mystocklist:
            print i
            self.drop_down_from_high(code=i, start='2017-01-01')
            print '\n'

    # 持股跌破均线
    def _break_line(self, codes, k_type):
        delta_day = 60 * 7 / 5
        end_day = datetime.date(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day)
        start_day = end_day - datetime.timedelta(delta_day)

        start_day = start_day.strftime("%Y-%m-%d")
        end_day = end_day.strftime("%Y-%m-%d")
        print start_day
        print end_day
        all_break = []

        for i in codes:
            try:
                df = ts.get_hist_data(code=i, start=start_day, end=end_day)
                if len(df)==0:
                    continue
            except Exception,e:
                print e
                continue
            else:
                self.working_count=self.working_count+1
                current = df['close'][0]
                ma5 = df['ma5'][0]
                ma10 = df['ma10'][0]
                ma20 = df['ma20'][0]
                ma_dict = {'5': ma5, '10': ma10, '20': ma20}
                ma_x = ma_dict[k_type]
                print ma_x
                if current < ma_x:
                    print i, " current: ", current
                    print self.base[self.base['code'] == i]['name'].values[0], " "

                    print "Break MA", k_type, "\n"
                    all_break.append(i)
        return all_break

    # 检查自己的持仓或者市场所有破位的
    def break_line(self, code, k_type='20',writeable=False):

        all_break = self._break_line(code, k_type)


        l=len(all_break)
        beaking_rate=l*1.00/self.working_count*100
        print "how many break: " ,l
        print "break Line rate " , beaking_rate
        if writeable:
            f=open(self.today+'break_line_'+k_type+'.csv','w')
            f.write("Breaking rate: %f\n\n" %beaking_rate)
            f.write('\n'.join(all_break))

            f.close()

    def _break_line_thread(self,codes,k_type):
        delta_day = 60 * 7 / 5
        end_day = datetime.date(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day)
        start_day = end_day - datetime.timedelta(delta_day)

        start_day = start_day.strftime("%Y-%m-%d")
        end_day = end_day.strftime("%Y-%m-%d")
        print start_day
        print end_day
        all_break = []
        for i in codes:
            try:
                df = ts.get_hist_data(code=i, start=start_day, end=end_day)
                if len(df)==0:
                    continue
            except Exception,e:
                print e
                continue
            else:
                self.working_count=self.working_count+1
                current = df['close'][0]
                ma5 = df['ma5'][0]
                ma10 = df['ma10'][0]
                ma20 = df['ma20'][0]
                ma_dict = {'5': ma5, '10': ma10, '20': ma20}
                ma_x = ma_dict[k_type]
                #print ma_x
                if current > ma_x:
                    print i, " current: ", current
                    print self.base[self.base['code'] == i]['name'].values[0], " "

                    print "Break MA", k_type, "\n"
                    all_break.append(i)
        q.put(all_break)

    def multi_thread(self):
        total=len(self.all_code)
        thread_num=10
        delta=total/thread_num
        delta_left=total%thread_num
        t=[]
        i=0
        for i in range(thread_num):

            sub_code=self.all_code[i*delta:(i+1)*delta]
            t_temp=Thread(target=self._break_line_thread,args=(sub_code,'20'))
            t.append(t_temp)
        if delta_left !=0:
            sub_code=self.all_code[i*delta:i*delta+delta_left]
            t_temp=Thread(target=self._break_line_thread,args=(sub_code,'20'))
            t.append(t_temp)

        for i in range(len(t)):
            t[i].start()

        for j in range(len(t)):
            t[j].join()
        result=[]
        print "working done"
        while not q.empty():
            result.append(q.get())
        ff=open(self.today+'_high_m20.csv','w')
        for kk in result:
            print kk
            for k in kk:
                ff.write(k)
                ff.write(',')
                ff.write(self.base[self.base['code']==k]['name'].values[0])
                ff.write('\n')

        ff.close()


    def big_deal(self,codes,vol,check_time):
        '''
        for code in codes:
            df=ts.get_sina_dd(code,vol,check_time)
            print df
        '''
        df=ts.get_sina_dd('603918','2017-04-22')
        print df

def main():
    if ts.__version__ != '0.7.5':
        print "Make sure using tushare 0.7.5"
        exit()
    currnet = os.getcwd()
    folder = os.path.join(currnet, 'data')
    if os.path.exists(folder) == False:
        os.mkdir(folder)
    os.chdir(folder)

    obj = select_class()
    #留下来的函数都是有用的
    # obj.count_area(writeable=True)
    #df=obj.get_area(u'广东',writeable=True)
    #obj.showInfo(df)
    #df=obj.get_area(u'深圳',writeable=True)
    #obj.showInfo(df)
    # obj.get_all_location()
    #obj.fetch_new_ipo(20170101,writeable=False)

    # obj.drop_down_from_high('2017-01-01','300580')
    #obj.loop_each_cixin()

    df=obj.get_all_code()
    result=obj.volume_calculate(df)

    # obj.write_to_text()
    # obj.read_csv()
    # obj.own_drop_down()
    # obj.volume_calculate()
    # obj.break_line()
    # obj.save_data_excel()
    #obj.break_line(mine=False,k_type='5')
    #obj.multi_thread()
    #code=obj.get_chengfenggu()
    #obj.break_line(code)
    #obj.big_deal('603918',400,'2017-04-22')

if __name__ == "__main__":
    start_time=datetime.datetime.now()
    main()
    end_time=datetime.datetime.now()
    print "time use : ", (end_time-start_time).seconds
