from socket import *
import json
from Cryptodome.Cipher import AES
import hashlib
from bitstring import BitArray

pad = (lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16).encode())


def return_bLK(Bit) :
    hash_val = Bit.bin
    return bToDecimal(hash_val[:7]), hash_val[7:87], hash_val[87:216]

def bToDecimal(b) :
    val = 0
    for i in range(len(b)) :
        if b[6-i] == '1' :
            val+=2^int(i)
    return val

def getMsg(user, addr) :
    msg = json.loads(user.recv(50000))
    return msg

def make_Encryption(key, word) :
    beforeCipher = word
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(beforeCipher)

def TSetRetrieve(Tset,stag) :
    V = []
    beta = 1
    i = 0
    while beta :
        print('In While')
        b, L, K = return_bLK(BitArray(hashlib.sha256(make_Encryption(stag,pad(str(i).encode()))).digest()))
        T = Tset[b]
        for pair in T :
            if pair == 0 :
                continue
            elif pair['label'] == L :
                v = pair['value']['eval'] ^ int(K,2)
                e = ''
                if len(bin(v)[2:]) != 129 :
                    beta = 0
                    e = bin(v)[2:]
                    while len(e) != 128 :
                        e = '0'+e
                else :
                    e = bin(v)[3:]
                y = pair['value']['xval']
                V.append([e,y])
        i+=1
    print('end While')
    return V

def Search(Tset,Xset,xtoken,Z,p) :
    E = set()
    V = TSetRetrieve(Tset,stag)
    tw1 = len(xtoken)
    print(2)
    if tw1 == 0 :
        for i in V :
            E.add(i[0])
    else :
        for ctr in range(tw1) :
            t = len(xtoken[ctr])
            ori_z = Z[ctr]
            y = V[ctr][1]
            xid = ori_z * y % p
            print("xid : ",xid)
            for i in range(t) :
                xtag = pow(xtoken[ctr][i],xid,p)
                print('xtag :',xtag)
                if xtag in Xset :
                    E.add(V[ctr][0])
                    break
                else :
                    print(0)
    return E


if __name__=="__main__" :
    getTSetClient = socket(AF_INET, SOCK_STREAM)
    getTSetClient.bind(('',8080))
    getTSetClient.listen(10)
    user, addr = getTSetClient.accept()
    Tset = getMsg(user, addr)
    Xset = set(getMsg(user, addr))
    Z = getMsg(user, addr)
    stag = user.recv(50000)
    xtoken = getMsg(user, addr)
    p = getMsg(user, addr)
    E = Search(Tset,Xset,xtoken,Z,p)
    print(E)
    user.sendall(json.dumps(list(E)).encode())
