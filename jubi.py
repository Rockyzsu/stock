# -*-coding=utf-8-*-
__author__ = 'Rocky'
'''
http://30daydo.com
Contact: weigesysu@qq.com
'''
import requests,random,hashlib,hmac
class Jubi_web():

    def __init__(self):
        pass

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
        url='https://www.jubi.com/api/v1/balance/'
        coin='btc'
        nonce=self.get_nonce()
        public_key=''
        private_key=''
        sha=self.sha_convert(private_key)
        #message=coin+'&'+nonce+'&'+public_key
        message='nonce='+nonce+'&'+'key='+public_key

        signature = hmac.new(sha, message, digestmod=hashlib.sha256).digest();

        req=requests.post(url,data={'signature':signature,'key':public_key,'nonce':nonce})
        print req.status_code
        print req.text


if __name__=='__main__':
    obj=Jubi_web()
    #print obj.sha_convert('5zi7w-4mnes-swmc4-egg9b-f2iqw-396z4-g541b')
    print obj.get_signiture()