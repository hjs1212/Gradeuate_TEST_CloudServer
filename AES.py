from Crypto.Cipher import AES
import random

pad = lambda s : s + (16 - len(s)%16) * chr(16 - len(s) % 16)
unpad = lambda s : s[0:-ord(s[len(s)-1:])]

k=hex(random.getrandbits(128))
k = k[18:]
print("k값 : ",k)
W = ['knife','blood','clothes','fingerprint']

for i in range(0,4):
    bW = pad(W[i]).encode('utf8')
    cipher = AES.new(k.encode('utf8'),AES.MODE_ECB)
    Ke = cipher.encrypt(bW)
    dec = cipher.decrypt(Ke) #호복

    print(unpad(dec).decode())
