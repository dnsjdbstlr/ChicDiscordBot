import pymysql

class Connection:
    def __init__(self):
        #self.host = '127.0.0.1'
        self.host    = '34.121.37.217'
        self.user    = 'chic'
        self.pw      = '9892'
        self.db      = 'chicBot'
        self.conn    = pymysql.connect(host=self.host, user=self.user, password=self.pw, database=self.db)
        self.cur     = self.conn.cursor(pymysql.cursors.DictCursor)
        print('[알림][DB에 성공적으로 연결되었습니다.]')

    def __del__(self):
        self.conn.close()
        print('[알림][DB 연결을 끊었습니다.]')

db = Connection()
def getConnection():
    db.conn.ping()
    return db.conn, db.cur
