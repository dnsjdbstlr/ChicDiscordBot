import json
import os
import requests
from datetime import datetime
from urllib import parse

# API키
dnf_token = os.environ['dnf_token']

# 서버 아이디
SERVER_NAME_TO_ID = {
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

SERVER_ID_TO_NAME = {
    'anton'   : '안톤',
    'bakal'   : '바칼',
    'cain'    : '카인',
    'casillas': '카시야스',
    'diregie' : '디레지에',
    'hilder'  : '힐더',
    'prey'    : '프레이',
    'siroco'  : '시로코'
}

def getItemsInfo(itemName, wordType='full', itemType=None):
    url = 'https://api.neople.co.kr/df/items'
    params = {
        'limit' : 30,
        'itemName' : itemName,
        'wordType' : wordType,
        'apikey' : dnf_token
    }
    response = requests.get(url=url, params=params)
    itemsInfo = response.json()

    # 결과
    resultItemsInfo = []

    for info in itemsInfo['rows']:
        if '[영혼]' in info['itemName']: continue
        if '[결투장]' in info['itemName']: continue
        if info['itemType'] in ['무기', '방어구', '액세서리', '추가장비'] and \
           info['itemRarity'] in ['레전더리', '에픽', '신화']:

            # 이름이 중복될 경우
            for item in resultItemsInfo:
                if info['itemName'] == item['itemName']:
                    continue

            # 특정 타입만 필요한 경우
            if itemType == info['itemType']:
                resultItemsInfo.append(info)
            else:
                resultItemsInfo.append(info)

    return resultItemsInfo

def getItemImageUrl(itemId):
    return f"https://img-api.neople.co.kr/df/items/{itemId}"

def getChrImageUrl(server, chrId):
    return f"https://img-api.neople.co.kr/df/servers/{SERVER_NAME_TO_ID[server]}/characters/{chrId}"

def getSimilarItemInfo(itemName):
    url = 'https://api.neople.co.kr/df/items'
    params = {
        'limit' : 1,
        'itemName' : itemName,
        'wordType' : 'front',
        'apikey' : dnf_token
    }
    response = requests.get(url=url, params=params)
    result = response.json()

    if not result['rows']: return None
    else: return result['rows'][0]

def getItemDetailInfo(itemId):
    url = f"https://api.neople.co.kr/df/items/{itemId}"
    params = {
        'apikey' : dnf_token
    }
    response = requests.get(url=url, params=params)
    return response.json()

def getItemsDetail(itemIds):
    url = 'https://api.neople.co.kr/df/multi/items?itemIds=' + itemIds + '&apikey=' + dnf_token
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

def getItemAuction(itemName):
    url = 'https://api.neople.co.kr/df/auction-sold?itemName=' + itemName + '&limit=100&wordType=match&apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data['rows']

def getShopItemInfo(itemId):
    url = 'https://api.neople.co.kr/df/items/' + itemId + '/shop?apikey=' + dnf_token
    response = requests.get(url=url)
    return json.loads(response.text)

def getSetItemIdList(setItemName):
    url = 'https://api.neople.co.kr/df/setitems?setItemName=' + setItemName + '&limit=30&wordType=full&apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data['rows']

def getSetItemInfo(setItemId):
    url = 'https://api.neople.co.kr/df/setitems/' + setItemId + '?apikey=' + dnf_token
    response = requests.get(url=url)
    return json.loads(response.text)

def getSetItemsInfo(setItemIds):
    url = 'https://api.neople.co.kr/df/multi/setitems?setItemIds=' + setItemIds + '&apikey=' + dnf_token
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
    url = 'https://api.neople.co.kr/df/servers/' + SERVER_NAME_TO_ID[server] + '/characters?characterName=' + name + '&wordType=' + wordType + '&limit=15&apikey=' + dnf_token
    response = requests.get(url=url)
    temp = json.loads(response.text)
    data = temp['rows']

    for i in data:
        chrIdList.append( {'server'         : SERVER_ID_TO_NAME[i['serverId']],
                           'characterId'    : i['characterId'],
                           'characterName'  : i['characterName'],
                           'level'          : str(i['level']),
                           'jobName'        : i['jobName'],
                           'jobGrowName'    : i['jobGrowName']} )

    return chrIdList

def getChrEquipItems(server, chrId):
    url = 'https://api.neople.co.kr/df/servers/' + SERVER_NAME_TO_ID[server] + '/characters/' + chrId + '/equip/equipment?apikey=' + dnf_token
    response = requests.get(url=url)
    return json.loads(response.text)

def getEquipActiveSet(itemIds):
    url = 'https://api.neople.co.kr/df/custom/equipment/setitems?itemIds=' + itemIds + '&apikey=' + dnf_token
    response = requests.get(url=url)
    return json.loads(response.text)

def getChrEquipCreature(server, chrId):
    url = 'https://api.neople.co.kr/df/servers/' + SERVER_NAME_TO_ID[server] + '/characters/' + chrId + '/equip/creature?apikey=' + dnf_token
    response = requests.get(url=url)
    return json.loads(response.text)

def getChrBuffCreature(server, chrId):
    url = f'https://api.neople.co.kr/df/servers/{SERVER_NAME_TO_ID[server]}/characters/{chrId}/skill/buff/equip/creature?apikey={dnf_token}'
    res = requests.get(url=url)
    return json.loads(res.text)

def getChrBuffEquip(server, chrId):
    url = 'https://api.neople.co.kr/df/servers/' + SERVER_NAME_TO_ID[server] + '/characters/' + chrId + '/skill/buff/equip/equipment?apikey=' + dnf_token
    response = requests.get(url=url)
    return json.loads(response.text)

def getChrStatInfo(server, chrId):
    url = 'https://api.neople.co.kr/df/servers/' + SERVER_NAME_TO_ID[server] + '/characters/' + chrId + '/status?apikey=' + dnf_token
    response = requests.get(url=url)
    return json.loads(response.text)

def getChrTimeLine(server, chrId, *code):
    today = datetime.today()
    startDate = str(today.year) + '-' + str(today.month) + '-01 00:00'
    endDate   = str(today.year) + '-' + str(today.month) + '-' + str(today.day) + ' ' + str(today.hour) + ':' + str(today.minute)

    codes = ''
    for i in code:
        codes += str(i)
        if i!= code[-1]:
            codes += ','

    url = 'https://api.neople.co.kr/df/servers/' + SERVER_NAME_TO_ID[server] + '/characters/' + chrId + '/timeline?limit=100&code=' + codes + '&startDate=' + startDate + '&endDate=' + endDate + '&apikey=' + dnf_token
    response = requests.get(url=url)
    data = json.loads(response.text)
    return data['timeline']['rows']

def getChrSkillStyle(server, chrId):
    url = 'https://api.neople.co.kr/df/servers/' + SERVER_NAME_TO_ID[server] + '/characters/' + chrId + '/skill/style?apikey=' + dnf_token
    response = requests.get(url=url)
    return json.loads(response.text)

def getChrEquipAvatar(server, chrId):
    url = 'https://api.neople.co.kr/df/servers/' + SERVER_NAME_TO_ID[server] + '/characters/' + chrId + '/equip/avatar?apikey=' + dnf_token
    response = requests.get(url=url)
    return json.loads(response.text)

def getChrBuffAvatar(server, chrId):
    url = f'https://api.neople.co.kr/df/servers/{SERVER_NAME_TO_ID[server]}/characters/{chrId}/skill/buff/equip/avatar?apikey={dnf_token}'
    response = requests.get(url=url)
    return json.loads(response.text)

def getSkillDetailInfo(jobId, skillId):
    url = 'https://api.neople.co.kr/df/skills/' + jobId + '/' + skillId + '?apikey=' + dnf_token
    response = requests.get(url=url)
    return json.loads(response.text)

def getSkillInfo(jobId, skillId):
    url = 'https://api.neople.co.kr/df/skills/' + jobId + '/' + skillId + '?apikey=' + dnf_token
    response = requests.get(url=url)
    return json.loads(response.text)
