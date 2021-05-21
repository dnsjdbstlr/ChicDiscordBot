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

c = Connection()

# # # 기 린 # # #
def getEpicRanks():
    conn, cur = c.getConnection()

    # 지난달 데이터 삭제
    sql = 'DELETE FROM epicRank WHERE date <= LAST_DAY(NOW() - interval 1 month)'
    cur.execute(sql)
    conn.commit()

    sql = 'SELECT * FROM epicRank WHERE date > LAST_DAY(NOW() - interval 1 month) AND date <= LAST_DAY(NOW())'
    cur.execute(sql)
    return cur.fetchall()

def getEpicRank(server, name):
    conn, cur = c.getConnection()
    sql = f'SELECT * FROM epicRank WHERE server=%s and name=%s'
    cur.execute(sql, (server, name))
    return cur.fetchone()

def updateEpicRank(server, name, count, channel):
    date = datetime.now().strftime('%Y-%m-%d')
    epicRank = getEpicRank(server, name)

    conn, cur = c.getConnection()
    if epicRank is None:
        sql = 'INSERT INTO epicRank (date, server, name, count, channel) values (%s, %s, %s, %s, %s)'
        cur.execute(sql, (date, server, name, count, channel))
    else:
        sql = 'UPDATE epicRank SET date=%s, count=%s, channel=%s WHERE server=%s and name=%s'
        cur.execute(sql, (date, count, channel, server, name))
    conn.commit()

# # # 시 세 # # #
def getAuction():
    conn, cur = c.getConnection()
    sql = 'SELECT * FROM auction'
    cur.execute(sql)
    return cur.fetchall()

def getTodayPrice(name):
    date = datetime.now().strftime('%Y-%m-%d')

    conn, cur = c.getConnection()
    sql = f"SELECT * FROM auction WHERE date=%s and name=%s"
    cur.execute(sql, (date, name))
    rs = cur.fetchone()
    return rs['price'] if rs is not None else None

def getLatestPrice(name):
    try:
        conn, cur = c.getConnection()
        sql = 'SELECT * FROM auction WHERE name=%s'
        cur.execute(sql, name)
        rs = cur.fetchall()
        return rs[-1]
    except: return None

def getPrevPrice(name):
    try:
        conn, cur = c.getConnection()
        sql = 'SELECT * FROM auction WHERE name=%s'
        cur.execute(sql, name)
        rs = cur.fetchall()
        return rs[-2]
    except: return None

def updateAuctionPrice(itemName, price):
    date = datetime.now().strftime('%Y-%m-%d')
    todayPrice = getTodayPrice(itemName)

    conn, cur = c.getConnection()
    if todayPrice is None:
        sql = 'INSERT INTO auction (date, name, price) values (%s, %s, %s)'
        cur.execute(sql, (date, itemName, price))
    else:
        sql = 'UPDATE auction SET price=%s WHERE date=%s and name=%s'
        cur.execute(sql, (price, date, itemName))
    conn.commit()

# # # 계 정 # # #
def iniAccount(did):
    conn, cur = c.getConnection()
    sql = 'INSERT INTO account values (%s, %s, %s, %s)'
    cur.execute(sql, (did, 10000000, datetime(9999, 12, 31), 0))
    conn.commit()

def getAccount(did):
    conn, cur = c.getConnection()
    sql = f'SELECT * FROM account WHERE did=%s'
    cur.execute(sql, did)
    return cur.fetchone()

def getGold(did):
    try:
        return getAccount(did)['gold']
    except:
        return None

def gainGold(did, gold):
    old = getGold(did)
    new = max(old + gold, 0)

    conn, cur = c.getConnection()
    sql = 'UPDATE account SET gold=%s WHERE did=%s'
    cur.execute(sql, (new, did))
    conn.commit()

def updateAccountCheck(did):
    today = datetime.now().strftime('%Y-%m-%d')
    account = getAccount(did)
    if account is None:
        iniAccount(did)

    conn, cur = c.getConnection()
    sql = 'UPDATE account SET checkDate=%s, checkCount=%s WHERE did=%s'
    cur.execute(sql, (today, account['checkCount'] + 1, did))
    conn.commit()

# # # 강 화 # # #
def iniReinforce(did, _id, name):
    conn, cur = c.getConnection()
    sql = f"INSERT INTO reinforce values (%s, %s, %s, %s, %s, %s)"
    _max = {'name' : name, 'value' : 0}
    _try = {'success' : 0, 'fail' : 0, 'destroy' : 0}
    cur.execute(sql, (did, _id, name, 0, json.dumps(_max, ensure_ascii=False), json.dumps(_try, ensure_ascii=False)))
    conn.commit()

def resetReinforce(did, _id, name):
    conn, cur = c.getConnection()
    sql = f"UPDATE reinforce SET id=%s, name=%s, value=%s WHERE did=%s"
    cur.execute(sql, (_id, name, 0, did))
    conn.commit()

def delReinforce(did):
    conn, cur = c.getConnection()
    sql = f"DELETE FROM reinforce WHERE did=%s"
    cur.execute(sql, did)
    conn.commit()

def getReinforce(did=None):
    conn, cur = c.getConnection()
    if did is None:
        sql = f"SELECT * FROM reinforce"
        cur.execute(sql)
        return cur.fetchall()
    else:
        sql = f"SELECT * FROM reinforce WHERE did=%s"
        cur.execute(sql, did)
        return cur.fetchone()

def isValidReinforce(did):
    reinforce = getReinforce(did)
    if reinforce is None:
        return False
    else:
        return True

def setReinforceValue(did, value):
    conn, cur = c.getConnection()
    sql = f"UPDATE reinforce SET value=%s WHERE did=%s"
    cur.execute(sql, (value, did))
    conn.commit()

def getReinforceMax(did):
    try:
        conn, cur = c.getConnection()
        sql = f"SELECT max FROM reinforce WHERE did=%s"
        cur.execute(sql, did)
        rs = cur.fetchone()
        return json.loads(rs['max'])
    except: return None

def setReinforceMax(did, _max):
    conn, cur = c.getConnection()
    sql = f"UPDATE reinforce SET max=%s WHERE did=%s"
    cur.execute(sql, (json.dumps(_max, ensure_ascii=False), did))
    conn.commit()

def getReinforceTry(did):
    try:
        conn, cur = c.getConnection()
        sql = f"SELECT try FROM reinforce WHERE did=%s"
        cur.execute(sql, did)
        rs = cur.fetchone()
        return json.loads(rs['try'])
    except: return None

def setReinforceTry(did, _try):
    conn, cur = c.getConnection()
    sql = f"UPDATE reinforce SET try=%s WHERE did=%s"
    cur.execute(sql, (json.dumps(_try, ensure_ascii=False), did))
    conn.commit()

def incReinforceTry(did, result):
    _try = getReinforceTry(did)
    if _try is not None:
        _try[result] += 1
        setReinforceTry(did, _try)

# 거래
def iniStock(did):
    stock   = json.dumps({'wallet' : []})
    history = json.dumps({'history': []})
    date = datetime.now().strftime('%Y-%m-%d')

    conn, cur = c.getConnection()
    sql = 'INSERT INTO stock values (%s, %s, %s, %s, %s)'
    cur.execute(sql, (did, stock, history, date, 0))
    conn.commit()

def getStock(did):
    conn, cur = c.getConnection()
    sql = 'SELECT * FROM stock WHERE did=%s'
    cur.execute(sql, did)
    return cur.fetchone()

def getStocks():
    conn, cur = c.getConnection()
    sql = 'SELECT * FROM stock'
    cur.execute(sql)
    return cur.fetchall()

def addStock(did, data):
    stock = getStock(did)
    wallet = json.loads(stock['wallet'])
    wallet['wallet'].append(data)

    history = {
        'date'      : datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'stock'     : data['stock'],
        'leverage'  : data['leverage'],
        'size'      : data['size'],
        'bid'       : data['bid'],
        'income'    : 0
    }
    addHistory(did, history)

    conn, cur = c.getConnection()
    sql = 'UPDATE stock SET wallet=%s WHERE did=%s'
    cur.execute(sql, (json.dumps(wallet, ensure_ascii=False), did))
    conn.commit()

def delStock(did, idx, price):
    stock = getStock(did)
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
    addHistory(did, history)
    del wallet['wallet'][idx]

    conn, cur = c.getConnection()
    sql = 'UPDATE stock SET wallet=%s WHERE did=%s'
    cur.execute(sql, (json.dumps(wallet, ensure_ascii=False), did))
    conn.commit()

def addHistory(did, data):
    stock = getStock(did)
    history = json.loads(stock['history'])
    if len(history['history']) >= 6:
        for i in range(1, 6):
            history['history'][i - 1] = history['history'][i]
        del history['history'][5]

    history['history'].append(data)

    conn, cur = c.getConnection()
    sql = 'UPDATE stock SET history=%s WHERE did=%s'
    cur.execute(sql, (json.dumps(history, ensure_ascii=False), did))
    conn.commit()

def setLiquidate(did, allowDate):
    conn, cur = c.getConnection()
    stock = getStock(did)

    wallet  = json.dumps({'wallet' : []})
    history = json.dumps({'history': []})

    sql = 'UPDATE stock SET wallet=%s, history=%s, allowDate=%s, liquidate=%s WHERE did=%s'
    cur.execute(sql, (wallet, history, allowDate, stock['liquidate'] + 1, did))
    conn.commit()

    sql = 'UPDATE account SET gold=%s WHERE did=%s'
    cur.execute(sql, (10000000, did))
    conn.commit()