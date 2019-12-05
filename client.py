import json
import random
import hashlib
import os
import sys
import Crypto.Util.number
from Cryptodome.Cipher import AES
from Crypto import Random
from bitstring import BitArray
from socket import *
from sympy import isprime

pad = (lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16).encode())
Tset = [[0] * 5 for i in range(128)]
Free = [[0,1,2,3,4] for i in range(128)]
binVal = ['0','1']

HOST = '127.0.0.1'
PORT = 8080
ADDR = (HOST, PORT)
Server = socket(AF_INET, SOCK_STREAM)
Server.connect(ADDR)

#q = 87398437484889945449419805561541091709369549757964871320294387262099269651453847881640404862414160814071801408087333245251478274970217057739636361127530868124559271120505522392522228767136266551217290422114205081174958418071006367457184946164770816540467804522804794070548390912774359964420395915489757563569
#g = 153252655045191169045820262078317928156224345493361493404845209018823600550144028350295788481133142626105475942350270963591288045332190282936609125689539726327297320876790929971125975583811566083242388803750900665421771613161248511098858830924584912395357566533897632838633211396254792888545673267599766796080
#p = 174796874969779890898839611123082183418739099515929742640588774524198539302907695763280809724828321628143602816174666490502956549940434115479272722255061736249118542241011044785044457534272533102434580844228410162349916836142012734914369892329541633080935609045609588141096781825548719928840791830979515127139

def OPRFSetup(t) :
    p = 0
    q = 0
    g = 0
    Cant = []
    while True :
        q = Crypto.Util.number.getPrime(t-1, randfunc=Crypto.Random.get_random_bytes)
        if q in Cant :
            continue
        else :
            Cant.append(q)
        p = 2 * q + 1
        if isprime(p) :
            break
        else :
            print('p is not Prime')
    print('p is Prime')
    while True :
        g = random.randint(2,p-2)
        a = pow(g,2, p)
        b = pow(g,q, p)

        if  a != 1 and b == 1 :
            break

        print('End')
    return p,g,q
p,g,q= OPRFSetup(1024)

class Value :
    def __init__(self,eval,xval) :
        self.eval = eval
        self.xval = xval

class Pair :
    def __init__(self, label, eval, xval) :
        self.label = label
        self.value = Value(eval,xval).__dict__

def sendMsg(line) :
    msg = json.dumps(line)
    Server.sendall(msg.encode())

def make_key() :
    k = '1'
    for i in range(15) :
        k = k + random.choice(binVal)
    return k.encode()



def OPRFKeyGen(k,l) :
    keyList = []
    binVal = ['0','1']
    for i in range(l) :
        val = "1"
        for count in range(1,k) :
            val = val + random.choice(binVal)
        keyList.append(int(val,2))
    return keyList

def G(p,g,k,x) :
    x = x
    y = g
    for i in range(len(k)) :
        if x[i] == '1' :
            y = pow(y,k[i],p)
    return y

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

def make_Encryption(key, word) :
    beforeCipher = word
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(beforeCipher)

def make_Decryption(key, afterCipher) :
	cipher = AES.new(key, AES.MODE_ECB)
	return cipher.decrypt(afterCipher)

def EEA(a, b):
	if not b:
		return [1, 0, a]
	x, y, d = EEA(b, a % b)
	return [y, x - (a // b) * y, d]

def inv(a, M):
	x, y, d = EEA(a, M)
	return x

def return_bLK(Bit) :
    hash_val = Bit.bin
    return bToDecimal(hash_val[:7]), hash_val[7:87], hash_val[87:216]

def bToDecimal(b) :
    val = 0
    for i in range(len(b)) :
        if b[6-i] == '1' :
            val+=2^int(i)
    return val

def EDBSetup(origin) :
    T = []
    W = origin.keys()
    Xset = set()
    State = {}
    ks = make_key()
    i = 0
    kd = OPRFKeyGen(128,64)
    kx = OPRFKeyGen(128,64)
    kz = OPRFKeyGen(128,64)
    for w in W :
        T.append([w])
        fileList = origin[w]
        ke = make_Encryption(ks,pad(w.encode()))
        for ctr in range(len(fileList)) :
            e = make_Encryption(ke,fileList[ctr].encode())
            xid = G(p,g,kd,BitArray(fileList[ctr].encode()).bin) % p
            z = G(p,g,kz,(BitArray(pad(w.encode())) ^ BitArray(pad(str(ctr).encode()))).bin)
            rev_z = inv(z,p)
            y = xid * rev_z
            T[i].append((e,y))
            xtag = pow(g,(G(p,g,kx,BitArray(pad(w.encode())).bin))*xid,p)
            Xset.add(xtag)
        State[w] = len(fileList)
        i+=1
    Tset, kt = TSetSetup(T,W)
    sendMsg(Tset)
    sendMsg(list(Xset))
    return ks, kt, kd, kx, kz, State

def TSetSetup(T,W) :
    kt = make_key()
    val = 0
    for w in W :
        stag = TsetGetTag(kt,w)
        V = T[val][1:]
        tw = len(V)
        for i in range(tw) :
            b, L, K = return_bLK(BitArray(hashlib.sha256(make_Encryption(stag,pad(str(i).encode()))).digest()))
            j = random.choice(Free[b])
            Free[b].remove(j)
            beta = '1'
            if i == (tw-1) :
                beta = '0'
            pair = Pair(L,int(beta+BitArray(V[i][0]).bin,2) ^ int(K,2),V[i][1])
            Tset[b][j] = pair.__dict__
        val+=1
    return Tset, kt

def ordList(msg,State) :
    ordWord = []
    for w in msg :
        for ord in range(len(ordWord)) :
            if State[w] < State[ordWord[ord]] :
                ordWord.insert(ord,w)
                break
        else :
            ordWord.append(w)
    return ordWord

def TsetGetTag(kt,w) :
    stag = make_Encryption(kt,pad(w.encode()))
    return stag

def Search(ks, kt, kd, kx, kz, State, msg) :
    w1 = msg[0]
    stag = TsetGetTag(kt,w1)
    xtoken = []
    Zet = []
    if len(msg) > 1 :
        ext = msg[1:]
        tw1 = State[w1]
        for ctr in range(tw1) :
            Zctr = G(p,g,kz,(BitArray(pad(w1.encode())) ^ BitArray(pad(str(ctr).encode()))).bin)
            Zet.append(Zctr)
            xtok = []
            for i in range(len(ext)) :
                val = pow(g,G(p,g,kx,BitArray(pad(ext[i].encode())).bin),p)
                xtok.append(val)
            xtoken.append(xtok)
    print(0)
    sendMsg(Zet)
    Server.sendall(stag)
    sendMsg(xtoken)
    sendMsg(p)
    msg = json.loads(Server.recv(50000))
    ke = make_Encryption(ks,pad(w1.encode()))
    fileList = []
    for file in msg :
        id = make_Decryption(ke,BitArray(bin=file).bytes).decode('utf-8')
        fileList.append(id)
    return fileList
if __name__ == '__main__' :
    '''
    ['cloakrooms', 'cohabitees', 'debutantes', 'debauchery', 'coastlands', 'babysitter', 'abhorrence']
    '''

    #State={'cloakrooms': 3, 'cohabitees': 2, 'debutantes': 3, 'debauchery': 1, 'coastlands': 4, 'babysitter': 3, 'abhorrence': 1}
    origin = getFile('./send/')
    ks, kt, kd, kx, kz, State = EDBSetup(origin)
    msg = ordList(input("Index Keyword : ").split(),State)
    fileList = Search(ks, kt, kd, kx, kz, State, msg)
    print(fileList)
