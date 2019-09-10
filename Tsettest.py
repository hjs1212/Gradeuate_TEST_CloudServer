import random
Tset = [[],[],[],[]]
Free = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
keyword = [['w1',['A1','C1','D1','Z1','A2','M1']],['w2',['A1','B1']],['w3',['B1','D1','F1','B3']],['w4',['D1','F1','E1','G1']]]
keyword2 = {'w1' : {'A1','C1','D1','Z1','A2','M1'}, 'w2':{'A1','B1'},'w3':{'B1','D1','F1','B3'},'w4' : {'D1','F1','E1','G1'}}
p = 43
q = 59
N = 2537
phi = (p-1) * (q-1)
e = 13
d = 937
pk = (N,e)
sk = (N,d,p,q)

def RSA_Enc(msg) :
    #print(msg)
    M = 0
    val = []
    for i in range(len(msg)) :
        M = ord(msg[i])
        M = (M**e) % N
        val.insert(0,M)
    return val

def RSA_Dec(msg) :
    #print(msg)
    string = ''
    for C in msg :
        M = (C**d) % N
        #print('M : ', M)
        string = chr(M) + string
    return string

'''
def Tset() :
    for i in keyword :
        key = RSA_Enc(i[0])
        for file in i[1] :
            pair = (key,file)
            val = random.choice(Free)
            Free.remove(val)
            j = val % 4
            B = val // 4
            print('B : ',B,'j : ', j,'pair : ',pair)
            Tset[B].insert(j, pair)
'''
def Tset2() :
    for i in keyword2.keys() :
        key = RSA_Enc(i)
        for file in keyword2[i] :
            pair = (key, file)
            val = random.choice(Free)
            Free.remove(val)
            j = val % 4
            B = val // 4
            #print('B : ',B,'j : ', j,'pair : ',pair)
            Tset[B].insert(j, pair)
    return Tset

def Tsolv2(Tset) :
    table = {}
    for pairs in Tset :
        for pair in pairs :
            #key = pair[0]
            key = RSA_Dec(pair[0])
            file = pair[1]
            if str(key) in table :
                table[str(key)].add(file)
            else :
                table[str(key)] = {file}

    print(table)

print(keyword2)
T = Tset2()
print(T)
Tsolv2(T)
