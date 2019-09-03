import socket
import json
import pymongo
import thread

get_keywordPort = 3996
get_fileNamePort = 4000
send_filePort = 4004

try :
    connection = pymongo.MongoClient('mongodb://127.0.0.1:27017')
except :
    print("MongoDB Connection Error")
    sys.exit()
else :
    print('MongoDB Connection Success')


if __name__ == '__main__' :
    get_keywordServer = socket(AF_INET, SOCK_STREAM)
    get_fileNameServer = socket(AF_INET, SOCK_STREAM)

    get_keywordServer.bind(('',get_keywordPort))
    get_fileNameServer.bind(('',get_fileNamePort))

    get_keywordServer.listen(10)
    get_fileNameServer.listen(10)
