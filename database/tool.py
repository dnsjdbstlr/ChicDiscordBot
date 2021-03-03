import json
from datetime import datetime
from database import connection

# # # 로 그 # # #
def log(message):
    commandList = ['!등급', '!캐릭터', '!장비', '!세트', '!시세', '!획득에픽', '!기린랭킹', '!주식', '!주식매수',
                   '!주식매도', '!주식랭킹', '!출석', '!강화설정', '!강화정보', '!강화', '!공개강화', '!청소']
    conn, cur = connection.getConnection()

    if message.content.split(' ')[0] in commandList:
        sql = 'INSERT INTO log (did, gid, command, time) values (%s, %s, %s, %s)'
        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur.execute(sql, (message.author.id, message.guild.id, message.content, date))
        conn.commit()

# # # 시 세 # # #
def getTodayPrice(name):
    date = datetime.now().strftime('%Y-%m-%d')

    conn, cur = connection.getConnection()
    sql = f"SELECT * FROM auction WHERE date=%s and name=%s"
    cur.execute(sql, (date, name))
    return cur.fetchone()

def getRecentPrice(name):
    try:
        conn, cur = connection.getConnection()
        sql = 'SELECT * FROM auction WHERE name=%s'
        cur.execute(sql, name)
        rs = cur.fetchall()
        return rs[-2]
    except: return None

def updateAuctionPrice(name, avgPrice):
    date = datetime.now().strftime('%Y-%m-%d')
    todayPrice = getTodayPrice(name)

    conn, cur = connection.getConnection()
    if todayPrice is None:
        sql = 'INSERT INTO auction (date, name, price) values (%s, %s, %s)'
        cur.execute(sql, (date, name, avgPrice))
        conn.commit()
    else:
        sql = 'UPDATE auction SET price=%s WHERE date=%s and name=%s'
        cur.execute(sql, (avgPrice, date, name))
        conn.commit()

# # # 기 린 # # #
def getEpic(server, name):
    conn, cur = connection.getConnection()
    sql = f'SELECT * FROM epic WHERE server=%s and name=%s'
    cur.execute(sql, (server, name))
    return cur.fetchone()

def updateEpicRank(server, name, gainEpicCount, channel):
    today = datetime.now().strftime('%Y-%m-%d')
    epic = getEpic(server, name)

    conn, cur = connection.getConnection()
    if epic is None:
        sql = 'INSERT INTO epic (date, server, name, count, channel) values (%s, %s, %s, %s, %s)'
        cur.execute(sql, (today, server, name, gainEpicCount, channel))
        conn.commit()
    else:
        sql = 'UPDATE epic SET count=%s, channel=%s, date=%s WHERE server=%s and name=%s'
        cur.execute(sql, (gainEpicCount, channel, today, server, name))
        conn.commit()

def getMonthlyEpicRank():
    conn, cur = connection.getConnection()
    sql = 'SELECT * FROM epic WHERE date > LAST_DAY(NOW() - interval 1 month) AND date <= LAST_DAY(NOW())'
    cur.execute(sql)
    return cur.fetchall()

# # # 주 식 # # #
def iniStock(did):
    conn, cur = connection.getConnection()
    sql = f'INSERT INTO stock (did, gold) values ({did}, {10000000})'
    cur.execute(sql)
    conn.commit()

def getStock(did):
    conn, cur = connection.getConnection()
    sql = f'SELECT * FROM stock WHERE did={did}'
    cur.execute(sql)
    return cur.fetchone()

def isValidStock(did):
    stock = getStock(did)
    if stock is not None:
        return True
    else:
        return False

def getGold(did):
    conn, cur = connection.getConnection()
    sql = f'SELECT * FROM stock WHERE did={did}'
    cur.execute(sql)
    rs = cur.fetchone()
    return rs['gold']

def gainGold(did, gold):
    old = getGold(did)
    new = max(old + gold, 0)

    conn, cur = connection.getConnection()
    sql = f'UPDATE stock SET gold={new} WHERE did={did}'
    cur.execute(sql)
    conn.commit()

# # # 출 석 # # #
def getDailyCheck(did):
    conn, cur = connection.getConnection()
    sql = f'SELECT * FROM dailyCheck WHERE did={did}'
    cur.execute(sql)
    return cur.fetchone()

def updateDailyCheck(did):
    conn, cur = connection.getConnection()
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

# # # 강 화 # # #
def iniReinforce(did, _id, name):
    conn, cur = connection.getConnection()
    sql = f"INSERT INTO reinforce values (%s, %s, %s, %s, %s, %s)"
    _max = {'name' : name, 'value' : 0}
    _try = {'success' : 0, 'fail' : 0, 'destroy' : 0}
    cur.execute(sql, (did, _id, name, 0, json.dumps(_max, ensure_ascii=False), json.dumps(_try, ensure_ascii=False)))
    conn.commit()

def resetReinforce(did, _id, name):
    conn, cur = connection.getConnection()
    sql = f"UPDATE reinforce SET id=%s, name=%s, value=%s WHERE did=%s"
    cur.execute(sql, (_id, name, 0, did))
    conn.commit()

def delReinforce(did):
    conn, cur = connection.getConnection()
    sql = f"DELETE FROM reinforce WHERE did={did}"
    cur.execute(sql)
    conn.commit()

def getReinforce(did):
    conn, cur = connection.getConnection()
    sql = f"SELECT * FROM reinforce WHERE did={did}"
    cur.execute(sql)
    return cur.fetchone()

def isValidReinforce(did):
    reinforce = getReinforce(did)
    if reinforce is None:
        return False
    else:
        return True

def setReinforceValue(did, value):
    conn, cur = connection.getConnection()
    sql = f"UPDATE reinforce SET value={value} WHERE did={did}"
    cur.execute(sql)
    conn.commit()

def getReinforceMax(did):
    try:
        conn, cur = connection.getConnection()
        sql = f"SELECT max FROM reinforce WHERE did={did}"
        cur.execute(sql)
        rs = cur.fetchone()
        return json.loads(rs['max'])
    except: return None

def setReinforceMax(did, _max):
    conn, cur = connection.getConnection()
    sql = f"UPDATE reinforce SET max=%s WHERE did={did}"
    cur.execute(sql, json.dumps(_max, ensure_ascii=False))
    conn.commit()

def getReinforceTry(did):
    try:
        conn, cur = connection.getConnection()
        sql = f"SELECT try FROM reinforce WHERE did={did}"
        cur.execute(sql)
        rs = cur.fetchone()
        return json.loads(rs['try'])
    except: return None

def setReinforceTry(did, _try):
    conn, cur = connection.getConnection()
    sql = f"UPDATE reinforce SET try=%s WHERE did={did}"
    cur.execute(sql, json.dumps(_try, ensure_ascii=False))
    conn.commit()

def incReinforceTry(did, result):
    _try = getReinforceTry(did)
    if _try is not None:
        _try[result] += 1
        setReinforceTry(did, _try)
