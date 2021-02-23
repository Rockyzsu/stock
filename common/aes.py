import sys
import base64
from Crypto.Cipher import AES
from Crypto import Random
import os
import base64
import json
from binascii import b2a_hex, a2b_hex


class AESDecrypt:

    def set_key(self,key):
        # key = ''
        self.key = self.add_to_16(key)

    def add_to_16(self, text):
        while len(text) % 16 != 0:
            text += '\0'
        return text.encode('utf8')

    def decode_base64(self, data):
        missing_padding = 4-len(data) % 4
        if missing_padding:
            data += '='*missing_padding
        return (data.encode('utf8'))

    def decrypt(self, encrypt_data):
        encrypt_data = self.decode_base64(encrypt_data)

        cipher = AES.new(self.key, mode=AES.MODE_ECB)
        result2 = base64.b64decode(encrypt_data)
        a = cipher.decrypt(result2)
        a = a.decode('utf-8', 'ignore')
        a = a.rstrip('\n')
        a = a.rstrip('\t')
        a = a.rstrip('\r')
        a = a.replace('\x06', '')
        a = a.replace('\x03', '')
        a = a.replace('\03', '')
        return a
