import json
import _pickle
import random
import hashlib
import os
from Cryptodome.Cipher import AES
from bitstring import BitArray
from socket import *

HOST = '127.0.0.1'
PORT = 8080
ADDR = (HOST, PORT)
sendTSetClient = socket(AF_INET, SOCK_STREAM)
sendMsgClient = socket(AF_INET, SOCK_STREAM)
getIndx = socket(AF_INET, SOCK_STREAM)

Tset = [[0] * 5 for i in range(128)]
Free = [[0,1,2,3,4] for i in range(128)]

pad = lambda s : s + (16 - len(s)%16) * chr(16 - len(s) % 16)

class Pair :
    def __init__(self, label, value) :
        self.label = label
        self.value = value

def make_Encryption(key, word) :
    beforeCipher = word
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(beforeCipher)

def make_Decryption(key, afterCipher) :
	cipher = AES.new(key, AES.MODE_ECB)
	return cipher.decrypt(afterCipher)

def bToDecimal(b) :
    val = 0
    for i in range(len(b)) :
        if b[6-i] == '1' :
            val+=2^int(i)
    return val

def XOR(id, K) :
    val = ''
    for i in range(129) :
        if id[i] != K[i] :
            val += '1'
        else :
            val += '0'
    return val

def return_bLK(Bit) :
    hash_val = Bit.bin
    return bToDecimal(hash_val[:7]), hash_val[7:87], hash_val[87:216]

def EDBSetup(origin) :
    T = {}
    Ks = 'idencryptionval0'.encode()
    for i in origin.keys() :
        key = make_Encryption(Ks,('000000'+i).encode())
        for id in origin[i] :
            file = BitArray(make_Encryption(key,id.encode())).bin
            if i in T :
                T[i].add(file)
            else :
                T[i] = {file}
    Tset, Kt = TSetSetup(T)
    return Tset, Ks, Kt

def TSetSetup(T) :
    Kt = []
    for w in T.keys() :
        print(w)
        stag = make_Encryption('iwanttogetstag00'.encode(),('000000'+w).encode())
        for i in range(len(T[w])) :
            indx = '1'
            if i == len(T[w])-1 :
                indx = '0'
            msg = pad(str(i)).encode()
            b, L, K = return_bLK(BitArray(hashlib.sha256(make_Encryption(stag,msg)).digest()))
            j = random.choice(Free[b])
            Free[b].remove(j)
            val = indx+list(T[w])[i]
            pair = Pair(L,XOR(val,K))
            Tset[b][j] = pair
    return Tset,'iwanttogetstag00'

def sendTset(connect_name, line) :
    msg = _pickle.dumps(line)
    connect_name.sendall(msg)

def sendMsg(connect_name, line) :
    msg = json.dumps(line)
    connect_name.sendall(msg)

def getMsg(user) :
    data = []
    while True :
        packet = user.recv(1024)
        if not packet : break
        data.append(packet)
    msg = _pickle.loads(b"".join(data))
    return msg

def getFile(PATH) :
    origin = {}
    for dir in os.listdir(PATH) :
        file = open(PATH+dir,'r')
        filename = dir[:-4]
        keywordlist = file.readline().split(',')
        for keyword in keywordlist :
            if keyword in origin :
                origin[keyword].append(filename)
            else :
                origin[keyword] = [filename]
    return origin

if __name__ == '__main__' :
    print('Start')
    origin = getFile('./send/')
    Tset, Ks, Kt = EDBSetup(origin)
    sendTSetClient.connect(ADDR)
    print(origin)
    print('Send Tset')
    print(Tset)
    if  Tset is not None:
        try :
            sendTset(sendTSetClient, Tset)
            sendTSetClient.close()
            msg = ('000000'+input("Index Keyword : ")).encode()
            encMsg = make_Encryption('iwanttogetstag00'.encode(),msg)
            sendMsgClient.connect(ADDR)
            sendTset(sendMsgClient, encMsg)
            sendMsgClient.close()
        except Exception as e :
            print('While transmitting, Problem detected : ',e)
    getIndx.connect(ADDR)
    indx = getMsg(getIndx)
    print(indx)
    getIndx.close()
    key = make_Encryption(Ks,msg)
    for bi in indx :
        id = make_Decryption(key,BitArray(bin=bi).bytes)
        print(id.decode())
