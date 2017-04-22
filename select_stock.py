# -*-coding=utf-8-*-
# 适用 tushare 0.7.5
__author__ = 'Rocky'
import tushare as ts
import pandas as pd
import os, sys, datetime, time,Queue
import numpy as np
from toolkit import Toolkit
from threading import Thread
reload(sys)
sys.setdefaultencoding('utf8')
q=Queue.Queue()

# 用来选股用的
# pd.set_option('max_rows',None)
# 缺陷： 暂时不能保存为excel
class select_class():
    def __init__(self):
        #self.base=ts.get_stock_basics()
        # print self.base
        # print self.base.index

        # 这里编码有问题
        # self.bases.to_excel('bases.xls')
        # self.bases.to_excel('base.xls',encoding='GBK')
        # self.bases.to_excel('111.xls',encoding='utf8')
        #self.base.to_csv('bases.csv')

        # 因为网速问题，手动从本地抓取

        # self.base=pd.read_csv('bases.csv',dtype={'code':np.str})
        # print self.base
        # self.today=datetime.datetime.strftime('%Y-%m-%d')
        self.today = time.strftime("%Y-%m-%d", time.localtime())
        self.base = pd.read_csv('bases.csv', dtype={'code': np.str})
        self.all_code = self.base['code'].values
        self.working_count=0
        # all_code=self.base.index.values
        # print self.base
        self.mystocklist = Toolkit.read_stock('mystock.csv')
        # print self.mystocklist

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

    def showInfo(self, df=None):
        if df == None:
            df = self.base
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
    #获取成分股
    def get_chengfenggu(self):
        s50=ts.get_sz50s()
        s50.to_excel('sz50.xls')
    # 显示次新股
    def cixingu(self, area, writeable=False):
        '''
        df=self.get_area(area)
        df_x=df.sort_values('timeToMarket',ascending=False)
        df_xx=df_x[:200]
        print df_xx
        if writeable:
            filename='cixin.csv'
            df_xx.to_csv(filename)
        '''
        # df_x= df.groupby('timeToMarket')
        # print df_x
        # df_x=df[df['timeToMarket']>'20170101']
        # print type( df['timeToMarket'])
        # df_time= df['timeToMarket']

        # new_df=pd.to_datetime(df_time)
        # print new_df
        # df_x= df[['area','timeToMarket']]
        # rint df_x.count()

        '''
        df_x=df.groupby('timeToMarket')
        print df_x
        for name,group in df_x:
            print name
            print group
        #df_x=df[df['timeToMarket']>'20170101']
        #print type( df['timeToMarket'])
        df_time= df['timeToMarket']
        new_df=pd.to_datetime(df_time)
        print new_df
        '''
        cixin = self.get_area(area).head(20)
        print cixin

    def output(self):
        print self.shenzhen()

    # 获取所有地区的分类个股
    def get_all_location(self):
        series = self.count_area()
        index = series.index
        for i in index:
            name = unicode(i)
            self.get_area(name, writeable=True)

    # 找出所有的次新股 默认12个月内
    def fetch_new_ipo(self, how_long=12, writeable=False):
        # 需要继续转化为日期类型
        # date=
        df = self.base.loc[self.base['timeToMarket'] > 20160101]
        df.sort_values('timeToMarket', inplace=True, ascending=False)
        if writeable == True:
            df.to_csv("New_IPO.csv")
        return df

    # 获取所有股票的代码,这个可以废掉
    '''
    def get_all_code(self):
            all_code=self.base['code'].values
            #all_code=self.base.index.values
            #print all_code
            return all_code
    '''

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
        df = self.fetch_new_ipo(writeable=True)
        all_code = df['code'].values
        print all_code
        # exit()
        percents = []
        for each in all_code:
            print each
            # print type(each)
            percent = self.drop_down_from_high('2016-01-01', each)
            percents.append(percent)

        df['Drop_Down'] = percents

        print df

        df.sort_values('Drop_Down', ascending=True, inplace=True)
        print df
        df.to_csv('drop_Down_cixin.csv')

    def get_macd(self, code):
        df = ts.get_k_data(code=code, start='2017-03-01')
        ma5 = df['close'][-5:].mean()
        ma10 = df['close'][-10:].mean()
        if ma5 > ma10:
            print code

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

    # 获取成交量的ma5 或者10
    def volume_calculate(self):
        delta_day = 60 * 7 / 5
        end_day = datetime.date(datetime.date.today().year, datetime.date.today().month, datetime.date.today().day)
        start_day = end_day - datetime.timedelta(delta_day)

        start_day = start_day.strftime("%Y-%m-%d")
        end_day = end_day.strftime("%Y-%m-%d")
        print start_day
        print end_day
        for each_code in self.all_code:
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

            if m5_volume_m > m10_volume_m and m5_volume_m > (2.0 * all_mean):
                print "m5 > m10 and m60 "
                print each_code,
                temp = self.base[self.base['code'] == each_code]['name'].values[0]
                print temp

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
    def break_line(self, mine=True, k_type='20'):

        if mine == True:
            all_break = self._break_line(self.mystocklist, k_type)
        else:
            all_break = self._break_line(self.all_code, k_type)


        l=len(all_break)
        beaking_rate=l*1.00/self.working_count*100
        print "how many break: " ,l
        print "break Line rate " , beaking_rate
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


'''

def _break_line_thread(codes,k_type):
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
                working_count=working_count+1
                current = df['close'][0]
                ma5 = df['ma5'][0]
                ma10 = df['ma10'][0]
                ma20 = df['ma20'][0]
                ma_dict = {'5': ma5, '10': ma10, '20': ma20}
                ma_x = ma_dict[k_type]
                print ma_x
                if current < ma_x:
                    print i, " current: ", current
                    print base[base['code'] == i]['name'].values[0], " "

                    print "Break MA", k_type, "\n"
                    all_break.append(i)
        q.put(all_break)

def multi_thread(self):
        total=len(all_code)
        thread_num=10
        delta=total/thread_num
        delta_left=total%thread_num
        t=[]
        i=0
        for i in range(delta):

            sub_code=all_code[i*delta:(i+1)*delta]
            t_temp=Thread(target=_break_line_thread,args=(sub_code))
            t.append(t_temp)
        if delta_left !=0:
            sub_code=self.all_code[i*delta:i*delta+delta_left]
            t_temp=Thread(target=_break_line_thread,args=(sub_code,'20'))
            t.append(t_temp)

        for i in range(len(t)):
            t[i].start()

        for j in range(len(t)):
            t[j].join()
        result=[]
        print "working done"
        while not q.empty():
            result.append(q.get())

        for k in result:
            print k

'''
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
    # obj.cixingu('深圳',writeable=True)
    # obj.shenzhen()
    # obj.showInfo()
    # obj.count_area(writeable=True)
    # obj.get_area(u'广东',writeable=True)
    # obj.get_all_location()
    # obj.cixingu('上海')
    # obj.fetch_new_ipo(writeable=True)
    # obj.drop_down_from_high('2017-01-01','300580')
    # obj.loop_each_cixin()
    # obj.debug_case()
    # obj.get_macd()

    # obj.write_to_text()
    # obj.read_csv()
    # obj.own_drop_down()
    # obj.volume_calculate()
    # obj.break_line()
    # obj.save_data_excel()
    #obj.break_line(mine=False,k_type='5')
    #obj.multi_thread()
    obj.get_chengfenggu()

if __name__ == "__main__":
    start_time=datetime.datetime.now()
    main()
    end_time=datetime.datetime.now()
    print "time use : ", (end_time-start_time).seconds
