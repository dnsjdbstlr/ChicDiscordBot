import json
from datetime import datetime
from Database import Connection

# # # 로 그 # # #
def log(message):
    commandList = ['!등급', '!캐릭터', '!장비', '!세트', '!시세', '!획득에픽', '!기린랭킹', '!주식', '!주식매수',
                   '!주식매도', '!주식랭킹', '!출석', '!강화설정', '!강화정보', '!강화', '!공개강화', '!청소']
    conn, cur = Connection.getConnection()

    if message.content.split(' ')[0] in commandList:
        sql = 'INSERT INTO log (did, gid, command, time) values (%s, %s, %s, %s)'
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(sql, (message.author.id, message.guild.id, message.content, date))
        conn.commit()

# # # 기 린 # # #
def getEpic(server, name):
    conn, cur = Connection.getConnection()
    sql = f'SELECT * FROM epic WHERE server=%s and name=%s'
    cur.execute(sql, (server, name))
    return cur.fetchone()

def updateEpicRank(server, name, gainEpicCount, channel):
    today = datetime.now().strftime('%Y-%m-%d')
    epic = getEpic(server, name)

    conn, cur = Connection.getConnection()
    if epic is None:
        sql = 'INSERT INTO epic (date, server, name, count, channel) values (%s, %s, %s, %s, %s)'
        cur.execute(sql, (today, server, name, gainEpicCount, channel))
        conn.commit()
    else:
        sql = 'UPDATE epic SET count=%s, channel=%s, date=%s WHERE server=%s and name=%s'
        cur.execute(sql, (gainEpicCount, channel, today, server, name))
        conn.commit()

def getMonthlyEpicRank():
    conn, cur = Connection.getConnection()
    sql = 'SELECT * FROM epic WHERE date > LAST_DAY(NOW() - interval 1 month) AND date <= LAST_DAY(NOW())'
    cur.execute(sql)
    return cur.fetchall()

# # # 시 세 # # #
def getAuction():
    conn, cur = Connection.getConnection()
    sql = 'SELECT * FROM auction'
    cur.execute(sql)
    return cur.fetchall()

def getTodayPrice(name):
    date = datetime.now().strftime('%Y-%m-%d')

    conn, cur = Connection.getConnection()
    sql = f"SELECT * FROM auction WHERE date=%s and name=%s"
    cur.execute(sql, (date, name))
    rs = cur.fetchone()
    return rs['price'] if rs is not None else None

def getLatestPrice(name):
    try:
        conn, cur = Connection.getConnection()
        sql = 'SELECT * FROM auction WHERE name=%s'
        cur.execute(sql, name)
        rs = cur.fetchall()
        return rs[-1]
    except: return None

def getPrevPrice(name):
    try:
        conn, cur = Connection.getConnection()
        sql = 'SELECT * FROM auction WHERE name=%s'
        cur.execute(sql, name)
        rs = cur.fetchall()
        return rs[-2]
    except: return None

def updateAuctionPrice(name, upgrade=-1):
    from Src import DNFAPI
    auction = DNFAPI.getItemAuctionPrice(name)
    if not auction: return False

    if upgrade != -1:
        name += f' +{upgrade}'
        auction = [i if i['upgrade'] == upgrade else None for i in auction]
        auction = list(filter(None, auction))

    p, c = 0, 0
    for i in auction:
        p += i['price']
        c += i['count']
    price = p // c

    # 데이터 저장
    date = datetime.now().strftime('%Y-%m-%d')
    todayPrice = getTodayPrice(name)

    conn, cur = Connection.getConnection()
    if todayPrice is None:
        sql = 'INSERT INTO auction (date, name, price) values (%s, %s, %s)'
        cur.execute(sql, (date, name, price))
        conn.commit()
    else:
        sql = 'UPDATE auction SET price=%s WHERE date=%s and name=%s'
        cur.execute(sql, (price, date, name))
        conn.commit()
    return auction

# # # 계 정 # # #
def iniAccount(did):
    conn, cur = Connection.getConnection()
    sql = 'INSERT INTO account values (%s, %s)'
    cur.execute(sql, (did, 10000000))
    conn.commit()

def getAccount(did):
    conn, cur = Connection.getConnection()
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

    conn, cur = Connection.getConnection()
    sql = 'UPDATE account SET gold=%s WHERE did=%s'
    cur.execute(sql, (new, did))
    conn.commit()

# # # 출 석 # # #
def getDailyCheck(did):
    conn, cur = Connection.getConnection()
    sql = 'SELECT * FROM dailyCheck WHERE did=%s'
    cur.execute(sql, did)
    return cur.fetchone()

def updateDailyCheck(did):
    conn, cur = Connection.getConnection()
    today = datetime.now().strftime('%Y-%m-%d')

    dailyCheck = getDailyCheck(did)
    if dailyCheck is None:
        sql = 'INSERT INTO dailyCheck (did, count, date) values (%s, %s, %s)'
        cur.execute(sql, (did, 1, today))
        conn.commit()
    else:
        sql = 'UPDATE dailyCheck SET count=%s, date=%s WHERE did=%s'
        cur.execute(sql, (dailyCheck['count'] + 1, today, did))
        conn.commit()

# # # 주 식 # # #
def iniStock(did):
    conn, cur = Connection.getConnection()
    sql = 'INSERT INTO stock (did, holding) VALUES (%s, %s)'
    cur.execute(sql, (did, json.dumps({'1' : None, '2' : None, '3' : None})))
    conn.commit()

def getStock(did=None):
    conn, cur = Connection.getConnection()
    if did is None:
        sql = 'SELECT * FROM stock'
        cur.execute(sql)
        return cur.fetchall()
    else:
        sql = 'SELECT * FROM stock WHERE did=%s'
        cur.execute(sql, did)
        return cur.fetchone()

def isValidStock(did):
    stock = getStock(did)
    if stock is not None:
        return True
    else:
        return False

# # # 강 화 # # #
def iniReinforce(did, _id, name):
    conn, cur = Connection.getConnection()
    sql = f"INSERT INTO reinforce values (%s, %s, %s, %s, %s, %s)"
    _max = {'name' : name, 'value' : 0}
    _try = {'success' : 0, 'fail' : 0, 'destroy' : 0}
    cur.execute(sql, (did, _id, name, 0, json.dumps(_max, ensure_ascii=False), json.dumps(_try, ensure_ascii=False)))
    conn.commit()

def resetReinforce(did, _id, name):
    conn, cur = Connection.getConnection()
    sql = f"UPDATE reinforce SET id=%s, name=%s, value=%s WHERE did=%s"
    cur.execute(sql, (_id, name, 0, did))
    conn.commit()

def delReinforce(did):
    conn, cur = Connection.getConnection()
    sql = f"DELETE FROM reinforce WHERE did=%s"
    cur.execute(sql, did)
    conn.commit()

def getReinforce(did=None):
    conn, cur = Connection.getConnection()
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
    conn, cur = Connection.getConnection()
    sql = f"UPDATE reinforce SET value=%s WHERE did=%s"
    cur.execute(sql, (value, did))
    conn.commit()

def getReinforceMax(did):
    try:
        conn, cur = Connection.getConnection()
        sql = f"SELECT max FROM reinforce WHERE did=%s"
        cur.execute(sql, did)
        rs = cur.fetchone()
        return json.loads(rs['max'])
    except: return None

def setReinforceMax(did, _max):
    conn, cur = Connection.getConnection()
    sql = f"UPDATE reinforce SET max=%s WHERE did=%s"
    cur.execute(sql, (json.dumps(_max, ensure_ascii=False), did))
    conn.commit()

def getReinforceTry(did):
    try:
        conn, cur = Connection.getConnection()
        sql = f"SELECT try FROM reinforce WHERE did=%s"
        cur.execute(sql, did)
        rs = cur.fetchone()
        return json.loads(rs['try'])
    except: return None

def setReinforceTry(did, _try):
    conn, cur = Connection.getConnection()
    sql = f"UPDATE reinforce SET try=%s WHERE did=%s"
    cur.execute(sql, (json.dumps(_try, ensure_ascii=False), did))
    conn.commit()

def incReinforceTry(did, result):
    _try = getReinforceTry(did)
    if _try is not None:
        _try[result] += 1
        setReinforceTry(did, _try)
