# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
import requests,random,hashlib,hmac
from toolkit import Toolkit
class Jubi_web():

    def __init__(self):
        self.public_key=Toolkit.getUserData('data.cfg')['public_key']
        self.private_key=Toolkit.getUserData('data.cfg')['private_key']

    def getContent(self):
        url='https://www.jubi.com/api/v1/trade_list'

        params_data={'key':'7a9wc-t3pkx-7snvp-3yb7w-m86g6-u5896-4ffcc','signature':'x'}
        s=requests.get(url=url,params=params_data)


    def getHash(self,s):
        m=hashlib.md5()
        m.update(s)
        return m.hexdigest()

    def sha_convert(self,s):
        return hashlib.sha256(self.getHash(s)).hexdigest()
    def get_nonce(self):
        lens=12
        return ''.join([str(random.randint(0, 9)) for i in range(lens)])

    def get_signiture(self):
        url='https://www.jubi.com/api/v1/ticker/'
        coin='zet'
        nonce=self.get_nonce()

        #sha=self.sha_convert(private_key)
        md5=self.getHash(self.private_key)
        message='nonce='+nonce+'&'+'key='+self.public_key
        #print message
        signature = hmac.new(md5, message, digestmod=hashlib.sha256).digest()
        #print signature

        #req=requests.post(url,data={'signature':signature,'key':public_key,'nonce':nonce,'coin':'zet'})
        req=requests.post(url,data={'coin':coin})
        print req.status_code
        print req.text

    def real_time_ticker(self,coin):
        url='https://www.jubi.com/api/v1/ticker/'
        data=requests.post(url,data={'coin':coin}).json()
        print data

    def real_time_depth(self,coin):
        url='https://www.jubi.com/api/v1/depth/'
        data=requests.post(url,data={'coin':coin}).json()
        print data
        data_bids=data['bids']
        data_asks=data['asks']
        print "bids"
        for i in data_bids:
            print i[0],
            print ' ',
            print i[1]
        print "asks"
        for j in data_asks:
            print j[0],
            print ' ',
            print j[1]

if __name__=='__main__':
    obj=Jubi_web()
    #print obj.get_signiture()
    obj.real_time_depth('zet')