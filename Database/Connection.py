import Ini
import pymysql

class Connection:
    def __init__(self):
        self.host    = Ini.db_host
        self.user    = Ini.db_user
        self.pw      = Ini.db_pw
        self.db      = Ini.db_name
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
