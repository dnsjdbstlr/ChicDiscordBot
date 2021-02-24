import json
from datetime import datetime
from database import connection

def getEpic(server, name):
    conn, cur = connection.getConnection()
    sql = f'SELECT * FROM epic WHERE server={server} and name={name}'
    cur.execute(sql)
    return cur.fetchone()

def getStock(did):
    conn, cur = connection.getConnection()
    sql = f'SELECT * FROM stock WHERE did={did}'
    cur.execute(sql)
    return cur.fetchone()

def iniStock(did):
    conn, cur = connection.getConnection()
    sql = f'INSERT INTO stock (did, gold) values ({did}, {10000000})'
    cur.execute(sql)
    conn.commit()

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

def getAdventure(did):
    conn, cur = connection.getConnection()
    sql = f'SELECT * FROM adventure WHERE did={did}'
    cur.execute(sql)
    return cur.fetchone()

def getInventory(did):
    adv = getAdventure(did)
    try:
        inv = json.loads(adv['inventory'])
        return inv['inventory']
    except:
        return None

def gainItem(did, *items):
    inv = getInventory(did)
    for i in items:
        inv.append(i)

    conn, cur = connection.getConnection()
    sql = f'UPDATE adventure SET inventory=%s WHERE did={did}'
    cur.execute(sql, json.dumps({'inventory' : inv}, ensure_ascii=False))
    conn.commit()

def removeItem(did, index, inv=None):
    if inv is None:
        inv = getInventory(did)
    del inv[index]

    conn, cur = connection.getConnection()
    sql = f'UPDATE adventure SET inventory=%s WHERE did={did}'
    cur.execute(sql, (json.dumps({'inventory' : inv}, ensure_ascii=False)))
    conn.commit()

def getEquipment(did, _type=None):
    adv = getAdventure(did)
    equipment = json.loads(adv['equipment'])
    if _type in ['weapon', 'accessory', 'additional']:
        return equipment[_type]
    else:
        return equipment

def setEquipment(did, item):
    equipment = getEquipment(did)
    if item['info']['id'] // 10000 == 1:
        equipment['weapon'] = item
    elif item['info']['id'] // 10000 == 2:
        equipment['accessory'] = item

    conn, cur = connection.getConnection()
    sql = f'UPDATE adventure SET equipment=%s WHERE did={did}'
    cur.execute(sql, json.dumps(equipment, ensure_ascii=False))
    conn.commit()
