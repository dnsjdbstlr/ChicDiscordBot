import json
import requests
from urllib import parse

# API키
apikey = 'GsjfwTqfwvgwdYj2nLNxo1wP0RVnkdLn'

# 서버 아이디
SERVER_ID = {
    '안톤'    : 'anton',
    '바칼'    : 'bakal',
    '카인'    : 'cain',
    '카시야스': 'casillas',
    '디레지에': 'diregie',
    '힐더'    : 'hilder',
    '프레이'  : 'prey',
    '시로코'  : 'siroco',
    '전체'    : 'all'
}

SERVERID_TO_NAME = {
    'anton'   : '안톤',
    'bakal'   : '바칼',
    'cain'    : '카인',
    'casillas': '카시야스',
    'diregie' : '디레지에',
    'hilder'  : '힐더',
    'prey'    : '프레이',
    'siroco'  : '시로코'
}

def getServerId(server):
    return SERVER_ID[server]

def getItemId(name):
    itemIdList = []

    name = parse.quote(name)
    url = 'https://api.neople.co.kr/df/items?itemName=' + name + '&limit=30&wordType=full' + '&apikey=' + apikey
    response = requests.get(url=url)
    data = json.loads(response.text)

    for i in data['rows']:
        if '[영혼]' in i['itemName']: continue
        if '[결투장]' in i['itemName']: continue
        if i['itemType'] in ['무기', '방어구', '액세서리', '추가장비'] and \
           i['itemRarity'] in ['레전더리', '에픽', '신화']:
            itemIdList.append({'itemId' : i['itemId'], 'itemName' : i['itemName']})
    return itemIdList

def getItemDetail(itemId):
    url = 'https://api.neople.co.kr/df/items/' + itemId + '?apikey=' + apikey
    response = requests.get(url=url)
    data = json.loads(response.text)
    return dict(data)

def getItemImageUrl(itemId):
    return 'https://img-api.neople.co.kr/df/items/' + itemId

def getItemStatInfo(itemStatus):
    itemStatInfo = ''
    for i in itemStatus:
        if i['name'] == '무게' or i['name'] == '내구도':
            continue
        itemStatInfo += i['name'] + ' : ' + str(i['value']) + '\r\n'
    return itemStatInfo

def getItemSkillLvInfo(jobName, levelRange):
    itemSkillInfo = ''
    if jobName == '공통':
        itemSkillInfo += '모든 직업 '
    else:
        itemSkillInfo += jobName

    for i in levelRange:
        if i['minLevel'] == i['maxLevel']:
            itemSkillInfo += str(i['minLevel']) + '레벨 모든 스킬 Lv+' + str(i['value']) + '\r\n'
        else:
            itemSkillInfo += str(i['minLevel']) + '~' + str(i['maxLevel']) + '레벨 모든 스킬 Lv+' + str(i['value']) + '\r\n'
    return itemSkillInfo

def getItemMythicInfo(options):
    itemMythicInfo = ''
    for i in options:
        itemMythicInfo += i['explainDetail'] + '\r\n'
    return itemMythicInfo

def getSetItemIdList(setItemName):
    setItemIdList = []

    url = 'https://api.neople.co.kr/df/setitems?setItemName=' + setItemName + '&limit=30&wordType=full&apikey=' + apikey
    response = requests.get(url=url)
    data = json.loads(response.text)

    for i in data['rows']:
        setItemIdList.append({'setItemId' : i['setItemId'], 'setItemName' : i['setItemName']})

    return setItemIdList

def getSetItemInfoList(setItemId):
    setItemInfoList = []
    setItemOptionList = []

    url = 'https://api.neople.co.kr/df/setitems/' + setItemId + '?apikey=' + apikey
    response = requests.get(url=url)
    data = json.loads(response.text)
    for i in data['setItems']:
        setItemInfoList.append({'slotName' : i['slotName'], 'itemId' : i['itemId'], 'itemName' : i['itemName'], 'itemRarity' : i['itemRarity']})

    for i in data['setItemOption']:
        explain = ''
        optionInfo = '\r\n'
        try:
            for j in i['status']:
                optionInfo += j['name'] + ' +' + str(j['value']) + '\r\n'
        except: pass
        try:
            explain = i['explain']
        except: pass

        setItemOptionList.append({'optionNo' : i['optionNo'], 'explain' : explain + optionInfo})

    return setItemInfoList, setItemOptionList

def getChrIdList(server, name):
    chrIdList = []

    name = parse.quote(name)
    url = 'https://api.neople.co.kr/df/servers/' + SERVER_ID[server] + '/characters?characterName=' + name + '&wordType=full&limit=30&apikey=' + apikey
    response = requests.get(url=url)
    temp = json.loads(response.text)
    data = temp['rows']

    for i in data:
        chrIdList.append( {'server' : SERVERID_TO_NAME[i['serverId']], 'characterId' : i['characterId'], 'characterName' : i['characterName'] ,'level' : str(i['level']), 'jobName' : i['jobName'], 'jobGrowName' : i['jobGrowName']} )

    return chrIdList

def getChrEquipItemInfoList(server, chrId):
    chrEquipItemIdList = []
    chrEquipItemEnchantInfo = []

    url = 'https://api.neople.co.kr/df/servers/' + SERVER_ID[server] + '/characters/' + chrId + '/equip/equipment?apikey=' + apikey
    response = requests.get(url=url)
    data = json.loads(response.text)

    for i in data['equipment']:
        if i['slotName'] == '칭호': continue
        enchantInfo = ''
        try:
            for j in i['enchant']['status']:
                enchantInfo += j['name'] + ' +' + str(j['value']) + '\r\n'
        except: pass
        chrEquipItemIdList.append(i['itemId'])
        chrEquipItemEnchantInfo.append({'enchant': enchantInfo, 'reinforce': i['reinforce'], 'refine': i['refine']})
        enchantInfo = ''

    return chrEquipItemIdList, chrEquipItemEnchantInfo

def getChrEquipSetItemInfo(chrEquipItemList):
    chrEquipSetItemName = []

    itemIds = ''
    for i in chrEquipItemList:
        itemIds += i
        if i != chrEquipItemList[-1]:
            itemIds += ','

    url = 'https://api.neople.co.kr/df/custom/equipment/setitems?itemIds=' + itemIds + '&apikey=' + apikey
    response = requests.get(url=url)
    temp = json.loads(response.text)

    try:
        data = temp['equipment']
        for i in data:
            chrEquipSetItemName.append((i['slotName'], i['itemName'], i['setItemName']))
    except:
        pass

    return chrEquipSetItemName

def getChrStatInfo(server, chrId):
    url = 'https://api.neople.co.kr/df/servers/' + SERVER_ID[server] +'/characters/' + chrId +'/status?apikey=' + apikey
    response = requests.get(url=url)
    temp = json.loads(response.text)
    chrBuffStatInfo = temp['buff'][0]['status']
    print(chrBuffStatInfo)