p = 43
q = 59
N = 2537
phi = (p-1) * (q-1)
e = 13
d = 937
pk = (N,e)
sk = (N,d,p,q)

def RSA_Enc(msg) :
    print(msg)
    M = 0
    val = []
    for i in range(len(msg)) :
        M = ord(msg[i])
        M = (M**e) % N
        val.insert(0,M)
    return val

def RSA_Dec(msg) :
    print(msg)
    string = ''
    for C in msg :
        M = (C**d) % N
        print('M : ', M)
        string = chr(M) + string
    return string

val = RSA_Enc('ABC')
print(val)
print(RSA_Dec(val))
