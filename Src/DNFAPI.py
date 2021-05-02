import Ini
import json
import requests
from urllib import parse
from datetime import datetime

# API키
dnf_token = Ini.dnf_token

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

def getItem(name, exactly=False, _type=None):
    name = parse.quote(name)
    wordType = 'full' if exactly is False else 'match'

    url = 'https://api.neople.co.kr/df/items?itemName=' + name + '&limit=30&wordType=' + wordType + '&apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)

    itemIdList = []
    for i in data['rows']:
        if '[영혼]' in i['itemName']  : continue
        if '[결투장]' in i['itemName']: continue
        if i['itemType'] in ['무기', '방어구', '액세서리', '추가장비'] and \
           i['itemRarity'] in ['레전더리', '에픽', '신화']:

            # 이름이 중복된 아이템은 리스트에 추가하지않음
            isOverride = False
            for j in itemIdList:
                if i['itemName'] == j['itemName']:
                    isOverride = True

            if not isOverride:
                # 특정 타입만 추가할 경우
                if _type is not None and _type == i['itemType']:
                    itemIdList.append(i)
                elif _type is None:
                    itemIdList.append(i)
    return itemIdList

def getItemImageUrl(itemId):
    return 'https://img-api.neople.co.kr/df/items/' + itemId

def getChrImageUrl(server, chrId):
    return 'https://img-api.neople.co.kr/df/servers/' + SERVER_ID.get(server) + '/characters/' + chrId

def getMostSimilarItem(name):
    name = parse.quote(name)
    url = 'https://api.neople.co.kr/df/items?itemName=' + name + '&q=trade:true&limit=1&wordType=front&apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)

    try:
        return data['rows'][0]
    except:
        return None

def getItemDetail(itemId):
    url = 'https://api.neople.co.kr/df/items/' + itemId + '?apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return dict(data)

def getItemsDetail(itemIds):
    items = ''
    for i in itemIds:
        items += i
        if i != itemIds[-1]: items += ','
    url = 'https://api.neople.co.kr/df/multi/items?itemIds=' + items + '&apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data['rows']

def getItemStatInfo(itemStatus):
    itemStatInfo = ''
    for i in itemStatus:
        if i['name'] in ['무게', '내구도']: continue
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

def getItemMythicInfo(options, buff=False):
    itemMythicInfo = ''
    for i in options:
        if buff:
            itemMythicInfo += i['buffExplainDetail'] + '\r\n'
        else:
            itemMythicInfo += i['explainDetail'] + '\r\n'
    return itemMythicInfo

def getItemAuctionPrice(itemName):
    url = 'https://api.neople.co.kr/df/auction-sold?itemName=' + itemName + '&limit=100&wordType=match&apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data['rows']

def getShopItemInfo(itemId):
    url = 'https://api.neople.co.kr/df/items/' + itemId + '/shop?apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data

def getSetItemIdList(setItemName):
    url = 'https://api.neople.co.kr/df/setitems?setItemName=' + setItemName + '&limit=30&wordType=full&apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data['rows']

def getSetItemInfoList(setItemId):
    url = 'https://api.neople.co.kr/df/setitems/' + setItemId + '?apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data

def getSetItemInfos(setItemIds):
    setItems = ''
    for i in setItemIds:
        setItems += i
        if i != setItemIds[-1]: setItems += ','

    url = 'https://api.neople.co.kr/df/multi/setitems?setItemIds=' + setItems + '&apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data['rows']

def getChrIdList(server, name):
    chrIdList = []

    if len(name) == 1:
        wordType = 'match'
    else:
        wordType = 'full'

    name = parse.quote(name)
    url = 'https://api.neople.co.kr/df/servers/' + SERVER_ID[server] + '/characters?characterName=' + name + '&wordType=' + wordType + '&limit=15&apikey=' + dnf_token
    response = requests.get(url=url)
    temp = json.loads(response.text)
    data = temp['rows']

    for i in data:
        chrIdList.append( {'server'         : SERVERID_TO_NAME[i['serverId']],
                           'characterId'    : i['characterId'],
                           'characterName'  : i['characterName'],
                           'level'          : str(i['level']),
                           'jobName'        : i['jobName'],
                           'jobGrowName'    : i['jobGrowName']} )

    return chrIdList

def getChrEquipItemInfoList(server, chrId):
    url = 'https://api.neople.co.kr/df/servers/' + SERVER_ID[server] + '/characters/' + chrId + '/equip/equipment?apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data

def getChrEquipSetItemInfo(chrEquipItemList):
    itemIds = ''
    for i in chrEquipItemList:
        itemIds += i
        if i != chrEquipItemList[-1]: itemIds += ','

    url = 'https://api.neople.co.kr/df/custom/equipment/setitems?itemIds=' + itemIds + '&apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data

def getChrEquipCreatureId(server, chrId):
    url = 'https://api.neople.co.kr/df/servers/' + SERVER_ID[server] + '/characters/' + chrId + '/equip/creature?apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data['creature']['itemId']

def getChrStatInfo(server, chrId):
    url = 'https://api.neople.co.kr/df/servers/' + SERVER_ID[server] +'/characters/' + chrId +'/status?apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data

def getChrTimeLine(server, chrId, *code):
    today = datetime.today()
    startDate = str(today.year) + '-' + str(today.month) + '-01 00:00'
    endDate   = str(today.year) + '-' + str(today.month) + '-' + str(today.day) + ' ' + str(today.hour) + ':' + str(today.minute)

    codes = ''
    for i in code:
        codes += str(i)
        if i!= code[-1]:
            codes += ','

    url = 'https://api.neople.co.kr/df/servers/' + SERVER_ID[server] + '/characters/' + chrId + '/timeline?limit=100&code=' + codes + '&startDate=' + startDate + '&endDate=' + endDate + '&apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data['timeline']['rows']

def getChrSkillStyle(server, chrId):
    url = 'https://api.neople.co.kr/df/servers/' + SERVER_ID[server] + '/characters/' + chrId + '/skill/style?apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data

def getChrBuffEquip(server, chrId):
    url = 'https://api.neople.co.kr/df/servers/' + SERVER_ID[server] + '/characters/' + chrId + '/skill/buff/equip/equipment?apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data

def getChrAvatarData(server, chrId):
    url = 'https://api.neople.co.kr/df/servers/' + SERVER_ID[server] + '/characters/' + chrId + '/equip/avatar?apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data

def getSkillDetailInfo(jobId, skillId):
    url = 'https://api.neople.co.kr/df/skills/' + jobId + '/' + skillId + '?apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data

def getSkillInfo(jobId, skillId):
    url = 'https://api.neople.co.kr/df/skills/' + jobId + '/' + skillId + '?apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data