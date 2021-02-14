import pymysql

# 설정
#host = '34.121.37.217'
host = '127.0.0.1'
user = 'chic'
pw   = '9892'
db   = 'chicBot'
charset = 'utf8'

def getConnection():
    conn = pymysql.connect(host=host, user=user, password=pw, database=db)
    cur  = conn.cursor(pymysql.cursors.DictCursor)
    return conn, cur