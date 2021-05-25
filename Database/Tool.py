import json
import os
import pymysql
from datetime import datetime

class Connection:
    def __init__(self):
        self.host    = '127.0.0.1'
        self.user    = os.environ['db_user']
        self.pw      = os.environ['db_pw']
        self.db      = os.environ['db']
        self.conn    = pymysql.connect(host=self.host, user=self.user, password=self.pw, database=self.db)
        self.cur     = self.conn.cursor(pymysql.cursors.DictCursor)
        print('[알림][DB에 성공적으로 연결되었습니다.]')

    def __del__(self):
        self.conn.close()
        print('[알림][DB 연결을 끊었습니다.]')

    def getConnection(self):
        self.conn.ping()
        return self.conn, self.cur

    # SEARCH
    def getEpicRanks(self):
        sql = 'DELETE FROM epicRank WHERE date <= LAST_DAY(NOW() - interval 1 month)'
        self.cur.execute(sql)
        self.conn.commit()

        sql = 'SELECT * FROM epicRank WHERE date > LAST_DAY(NOW() - interval 1 month) AND date <= LAST_DAY(NOW())'
        self.cur.execute(sql)
        return self.cur.fetchall()

    def getEpicRank(self, server, name):
        sql = f'SELECT * FROM epicRank WHERE server=%s and name=%s'
        self.cur.execute(sql, (server, name))
        return self.cur.fetchone()

    def updateEpicRank(self, server, name, count, channel):
        date = datetime.now().strftime('%Y-%m-%d')
        epicRank = self.getEpicRank(server, name)

        if epicRank is None:
            sql = 'INSERT INTO epicRank (date, server, name, count, channel) values (%s, %s, %s, %s, %s)'
            self.cur.execute(sql, (date, server, name, count, channel))
        else:
            sql = 'UPDATE epicRank SET date=%s, count=%s, channel=%s WHERE server=%s and name=%s'
            self.cur.execute(sql, (date, count, channel, server, name))
        self.conn.commit()

    # AUCTION
    def getTodayPrice(self, name):
        date = datetime.now().strftime('%Y-%m-%d')
        sql = f"SELECT * FROM auction WHERE date=%s and name=%s"
        self.cur.execute(sql, (date, name))
        rs = self.cur.fetchone()
        return rs.get('price')

    def getLatestPrice(self, name):
        try:
            sql = 'SELECT * FROM auction WHERE name=%s'
            self.cur.execute(sql, name)
            rs = self.cur.fetchall()
            return rs[-1]
        except: return None

    def getPrevPrice(self, name):
        try:
            sql = 'SELECT * FROM auction WHERE name=%s'
            self.cur.execute(sql, name)
            rs = self.cur.fetchall()
            return rs[-2]
        except: return None

    def updateAuctionPrice(self, itemName, price):
        date = datetime.now().strftime('%Y-%m-%d')
        todayPrice = self.getTodayPrice(itemName)

        if todayPrice is None:
            sql = 'INSERT INTO auction (date, name, price) values (%s, %s, %s) '
            self.cur.execute(sql, (date, itemName, price))
        else:
            sql = 'UPDATE auction SET price=%s WHERE date=%s and name=%s'
            self.cur.execute(sql, (price, date, itemName))
        self.conn.commit()

    # ACCOUNT
    def iniAccount(self, did):
        sql = 'INSERT INTO account values (%s, %s, %s, %s)'
        self.cur.execute(sql, (did, 10000000, datetime(9999, 12, 31), 0))
        self.conn.commit()

    def getAccount(self, did):
        sql = f'SELECT * FROM account WHERE did=%s'
        self.cur.execute(sql, did)
        return self.cur.fetchone()

    def getAccounts(self):
        sql = f'SELECT * FROM account'
        self.cur.execute(sql)
        return self.cur.fetchall()

    def getGold(self, did):
        try:    return self.getAccount(did)['gold']
        except: return None

    def gainGold(self, did, gold):
        old = self.getGold(did)
        new = max(old + gold, 0)

        sql = 'UPDATE account SET gold=%s WHERE did=%s'
        self.cur.execute(sql, (new, did))
        self.conn.commit()

    def updateDailyCheck(self, did):
        today = datetime.now().strftime('%Y-%m-%d')
        account = self.getAccount(did)
        if account is None:
            self.iniAccount(did)

        sql = 'UPDATE account SET checkDate=%s, checkCount=%s WHERE did=%s'
        self.cur.execute(sql, (today, account['checkCount'] + 1, did))
        self.conn.commit()

    # REINFORCE
    def setReinforce(self, did, itemId=None, itemName=None, value=None, _max=None, _try=None):
        reinforce = self.getReinforce(did)
        if reinforce is None:
            sql = 'INSERT INTO reinforce values (%s, %s, %s, %s, %s, %s)'
            _max = {
                'itemName': itemName,
                'value': 0
            }
            _try = {
                'success': 0,
                'fail': 0,
                'destroy': 0
            }
            self.cur.execute(sql, (did, itemId, itemName, value,
                                   json.dumps(_max, ensure_ascii=False), json.dumps(_try, ensure_ascii=False)))
        else:
            sql = 'UPDATE reinforce SET itemId=%s, itemName=%s, value=%s, max=%s, try=%s WHERE did=%s'
            itemId = reinforce['itemId'] if itemId is None else itemId
            itemName = reinforce['itemName'] if itemName is None else itemName
            value = reinforce['value'] if value is None else value
            _max = reinforce['max'] if _max is None else json.dumps(_max, ensure_ascii=False)
            _try = reinforce['try'] if _try is None else json.dumps(_try, ensure_ascii=False)
            self.cur.execute(sql, (itemId, itemName, value, _max, _try, did))
        self.conn.commit()

    def getReinforce(self, did):
        sql = 'SELECT * FROM reinforce WHERE did=%s'
        self.cur.execute(sql, did)
        return self.cur.fetchone()

    def getReinforces(self):
        sql = f"SELECT * FROM reinforce"
        self.cur.execute(sql)
        return self.cur.fetchall()

    # FUTURE TRADING
    def iniStock(self, did):
        stock   = json.dumps({'wallet' : []})
        history = json.dumps({'history': []})
        date = datetime.now().strftime('%Y-%m-%d')

        sql = 'INSERT INTO stock values (%s, %s, %s, %s, %s)'
        self.cur.execute(sql, (did, stock, history, date, 0))
        self.conn.commit()

    def getStock(self, did):
        sql = 'SELECT * FROM stock WHERE did=%s'
        self.cur.execute(sql, did)
        return self.cur.fetchone()

    def getStocks(self):
        sql = 'SELECT * FROM stock'
        self.cur.execute(sql)
        return self.cur.fetchall()

    def addStock(self, did, data):
        stock = self.getStock(did)
        wallet = json.loads(stock['wallet'])
        wallet['wallet'].append(data)

        history = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stock': data['stock'],
            'leverage': data['leverage'],
            'size': data['size'],
            'bid': data['bid'],
            'income': 0
        }
        self.addHistory(did, history)

        sql = 'UPDATE stock SET wallet=%s WHERE did=%s'
        self.cur.execute(sql, (json.dumps(wallet, ensure_ascii=False), did))
        self.conn.commit()

    def delStock(self, did, idx, price):
        stock = self.getStock(did)
        wallet = json.loads(stock['wallet'])

        data = wallet['wallet'][idx]
        income = (price - data['bid']) * data['size'] * data['leverage']

        history = {
            'date'      : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'stock'     : data['stock'],
            'leverage'  : -data['leverage'],
            'size'      : data['size'],
            'bid'       : price,
            'income'    : income
        }
        self.addHistory(did, history)
        del wallet['wallet'][idx]

        sql = 'UPDATE stock SET wallet=%s WHERE did=%s'
        self.cur.execute(sql, (json.dumps(wallet, ensure_ascii=False), did))
        self.conn.commit()

    def addHistory(self, did, data):
        stock = self.getStock(did)
        history = json.loads(stock['history'])
        if len(history['history']) >= 6:
            for i in range(1, 6):
                history['history'][i - 1] = history['history'][i]
            del history['history'][5]

        history['history'].append(data)

        sql = 'UPDATE stock SET history=%s WHERE did=%s'
        self.cur.execute(sql, (json.dumps(history, ensure_ascii=False), did))
        self.conn.commit()

    def setLiquidate(self, did, allowDate):
        stock   = self.getStock(did)
        wallet  = json.dumps({'wallet': []})
        history = json.dumps({'history': []})

        sql = 'UPDATE stock SET wallet=%s, history=%s, allowDate=%s, liquidate=%s WHERE did=%s'
        self.cur.execute(sql, (wallet, history, allowDate, stock['liquidate'] + 1, did))
        self.conn.commit()

        sql = 'UPDATE account SET gold=%s WHERE did=%s'
        self.cur.execute(sql, (10000000, did))
        self.conn.commit()

# 일반 커넥션
c = Connection()

# 스레드에서 사용할 커넥션
tc = Connection()