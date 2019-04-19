# -*- coding:utf-8 -*-
import base64
from Crypto.Cipher import AES
from Crypto import Random

pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
unpad = lambda s : s[:-ord(s[len(s)-1:])]
class AESCipher:
    def __init__(self):
        self.key = pad('opadmin')

    def encrypt(self, pwd):
        raw = pad(pwd)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.urlsafe_b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc_pwd):
        enc = base64.urlsafe_b64decode(enc_pwd.encode('utf-8'))
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[16:]))

if __name__ == "__main__":
    a = AESCipher()
    print(a.encrypt('abc123'))
    'vjuEBG6EwkG7knome63cfIuXjl9LvTXeK8myhmyDSec='
    print(a.decrypt('vjuEBG6EwkG7knome63cfIuXjl9LvTXeK8myhmyDSec='))