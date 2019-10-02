from socket import *
import json
import _pickle
from Cryptodome.Cipher import AES
import hashlib
from bitstring import BitArray

pad = lambda s : s + (16 - len(s)%16) * chr(16 - len(s) % 16)

class Pair :
    def __init__(self, label, value) :
        self.label = label
        self.value = value

def sendMsg(connect_name, line) :
    msg = _pickle.dumps(line)
    connect_name.sendall(msg)

def getTset(user, addr) :
    data = []
    while True :
        packet = user.recv(1024)
        if not packet : break
        data.append(packet)
    msg = _pickle.loads(b"".join(data))
    return msg

def getMsg(user, addr) :
    msg = json.loads(user.recv(1024).decode())
    return msg

def make_Encryption(key, word) :
	beforeCipher = word
	cipher = AES.new(key, AES.MODE_ECB)
	return cipher.encrypt(beforeCipher)

def make_Decryption(key, afterCipher) :
	cipher = AES.new(key, AES.MODE_ECB)
	return cipher.decrypt(afterCipher)

def XOR(id, K) :
    val = ''
    for i in range(129) :
        if id[i] != K[i] :
            val += '1'
        else :
            val += '0'
    return val

def bToDecimal(b) :
    val = 0
    for i in range(len(b)) :
        if b[6-i] == '1' :
            val+=2^int(i)
    return val

def return_bLK(Bit) :
    hash_val = Bit.bin
    return bToDecimal(hash_val[:7]), hash_val[7:87], hash_val[87:216]

def TSetRetrieve(Tset, stag) :
    table = set()
    indx = 1
    now = 0
    while indx == 1 :
        msg = pad(str(now)).encode()
        b, L, K = return_bLK(BitArray(hashlib.sha256(make_Encryption(stag,msg)).digest()))
        T = Tset[b]
        for j in range(len(T)) :
            if T[j]== 0 or T[j].label != L :
                continue
            value = XOR(T[j].value, K)
            if value[0] != '1' :
                indx = 0
            table.add(value[1:])
        now+=1
    return table


if __name__ == '__main__' :
    getTSetClient = socket(AF_INET, SOCK_STREAM)
    getTSetClient.bind(('',8080))
    getTSetClient.listen(10)
    Tset = {}
    try :
        user, addr = getTSetClient.accept()
        Tset = getTset(user, addr)
        print(Tset)
        user, addr = getTSetClient.accept()
        word = getTset(user, addr)
        table = TSetRetrieve(Tset,word)
        user, addr = getTSetClient.accept()
        sendMsg(user,table)
    except Exception as e :
        print('out : ', e)
    else :
        getTSetClient.close()
    print('Server closed')
