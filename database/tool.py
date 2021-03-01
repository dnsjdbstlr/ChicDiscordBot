import json
from datetime import datetime
from database import connection

# # # 기 린 # # #
def getEpic(server, name):
    conn, cur = connection.getConnection()
    sql = f'SELECT * FROM epic WHERE server={server} and name={name}'
    cur.execute(sql)
    return cur.fetchone()

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
