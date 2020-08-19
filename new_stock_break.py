# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
# 分析新股的开板时机
import tushare as ts
import os
import matplotlib.pyplot as plt

class NewStockBreak():
    def __init__(self,start_date=20170101,end_date=20170401):
        #为了文件整齐，新建一个文件夹data用来专门存放数据
        current = os.getcwd()
        folder = os.path.join(current, 'new_stock')
        if os.path.exists(folder) == False:
            os.mkdir(folder)
        os.chdir(folder)
        #调用tushare接口，获取A股信息
        df0=ts.get_stock_basics()
        # df0=pd.read_csv('bases.csv',dtype={'code':np.str})
        self.bases=df0.sort_values('timeToMarket',ascending=False)

        #获取样本， 获取最近一个年的新股情况
        self.cxg=self.bases[(self.bases['timeToMarket']>start_date) & (self.bases['timeToMarket']<end_date)]
        # self.codes= self.cxg['code'].values 官方接口修改
        self.codes = self.cxg.index.values

    def calc_open_by_percent(self,code):
        # 计算换手率
        cont=100000000
        #total_vol=self.bases[self.bases['code']==code]['totals'].values[0]
        acutal_vol=self.bases.loc[code]['outstanding']
        all_vol= acutal_vol*cont
        df_k_data=ts.get_k_data(code)
        i=1
        found = False
        df_k_data=df_k_data.sort_index(axis=0,ascending=True,by=['date'])
        while i<365:
            try:
                s=df_k_data.iloc[i]

            except IndexError:
                print('single positional indexer is out-of-bounds')
                break
            except Exception as e:
                print(e)
                break
            else:
                if s['high']!=s['low']:
                    found = True
                    break
                i=i+1
        if found:
            date_end=df_k_data.iloc[i]['date']
            date_start=df_k_data.iloc[0]['date']
            df3=df_k_data[(df_k_data['date']>=date_start) & (df_k_data['date']<=date_end)]
            v_total_break=df3['volume'].sum()
            day=len(df3)
            rate=round(v_total_break*100*100.00/all_vol,2) #手和股 注意
        else:
            rate,day = 0,0
        # 换手率与天数
        return rate,day


    def calc_open_day(self,code):
        cont=100000000
        #total_vol=self.bases[self.bases['code']==code]['totals'].values[0]
        acutal_vol=self.bases[self.bases['code']==code]['outstanding'].values[0]
        all_vol= acutal_vol*cont
        #df= ts.get_hist_data(code)
        df1=ts.get_k_data(code)
        if len(df1)<3:
            return None
        #print(df1.info())
        #df1=df.reset_index()
        #print(df1)
        start=df1['date'].values[0]
        print('Start day:', start)
        df2= df1[(df1['close']==df1['low']) & (df1['high']==df1['low'])]
        print(self.bases[self.bases['code']==code]['name'].values[0])
        end=df2['date'].values[-1]
        print("Break day" , end)

        df3=df1[(df1['date']>=start) & (df1['date']<=end)]
        v_total_break=df3['volume'].sum()
        l=len(df3)
        print(l)
        print(v_total_break)
        rate=v_total_break*100*100.00/all_vol #手和股 注意
        print(round(rate,6))
        return rate,l

    def testcase(self):
        #self.calc_open_day('603096')
        result=[]
        max_line=[]
        k=[]
        for i in self.codes:
            t,l=self.calc_open_day(i)
            if t is not None:
                result.append(t)
                max_line.append({i:l})
                k.append(l)
        x=range(len(result))
        #print(x)
        #print(result)
        plt.bar(x,result)
        plt.show()
        sum=0
        for i in result:
            sum=sum+i

        avg=sum*1.00/len(result)
        print(avg)
        max_v=max(k)
        print(max_v)
        print(max_line)

    def getData(self,filename):
        result=[]
        max_line=[]
        k=[]
        for i in self.codes:
            print(f'正处理{i}')
            name=self.bases.loc[i]['name']
            rate,day=self.calc_open_by_percent(i)
            if rate:
                result.append(rate)
                max_line.append([name,day,rate])
                k.append(day)

        #作图用的
        #x=range(len(result))
        #print(x)
        #print(result)
        #plt.bar(x,result)
        #lt.show()

        with open(filename,'w') as f:
            for x in max_line:
                #f.write(';'.join(x))
                f.write(x[0])
                f.write(';')
                f.write(str(x[1]))
                f.write(';')
                f.write(str(x[2]))
                f.write('\n')


def main():
    obj=NewStockBreak(start_date=20200101,end_date=20200701)
    obj.getData('cxg.txt')

if __name__ == '__main__':
    main()
