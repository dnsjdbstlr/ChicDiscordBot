import discord
import asyncio
import re
from src import DNFAPI
from database import Tool

# # # 선 택 # # #
async def getSelectionFromChrIdList(bot, ctx, chrIdList):
    await ctx.message.delete()

    # 여러개가 검색됬을 경우
    if len(chrIdList) >= 2:
        embed = discord.Embed(title='알고싶은 캐릭터의 번호를 입력해주세요!', description='15초만 기다려드릴거에요. 빠르게 골라주세요!')
        for i in range(len(chrIdList)):
            value = 'Lv. ' + chrIdList[i]['level'] + ' ' + chrIdList[i]['characterName'] + '\r\n' + \
                    chrIdList[i]['server'] + ' | ' + chrIdList[i]['jobGrowName']
            embed.add_field(name='> ' + str(i + 1), value=value)
        embed.set_footer(text='가장 뒤에 서버 이름을 적으면 해당 서버만 검색해요!')
        selection = await ctx.channel.send(embed=embed)

        ### 반응을 대기함 ###
        try:
            def check(m):
                return ctx.channel.id == m.channel.id and ctx.message.author == m.author
            result = await bot.wait_for('message', check=check, timeout=15)

        ### 시간 종료 ###
        except asyncio.TimeoutError:
            await selection.delete()
            await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
            return False

        ### 입력했을 경우 ###
        else:
            await selection.delete()
            await result.delete()
            try:
                index = int(result.content) - 1
                server, chrId, name = chrIdList[index]['server'], chrIdList[index]['characterId'], chrIdList[index]['characterName']
            except:
                await ctx.channel.send('> 제대로 입력해주셔야해요! 다시 시도해주세요!')
                return False

    # 한 개가 검색됬을 경우
    else:
        try:
            server, chrId, name = chrIdList[0]['server'], chrIdList[0]['characterId'], chrIdList[0]['characterName']
        except:
            await ctx.channel.send('> 해당 캐릭터를 찾을 수 없어요. 다시 한번 확인해주세요!')
            return False

    return server, chrId, name

async def getSelectionFromItemIdList(bot, ctx, itemList, title=None, description=None):
    await ctx.message.delete()

    if not len(itemList):
        await ctx.channel.send('> 해당 장비를 찾을 수 없어요.\r\n> 장비 이름을 확인하고 다시 불러주세요!')
        return False

    if len(itemList) >= 2:
        if title is None or description is None:
            embed = discord.Embed(title='알고싶은 장비 아이템의 번호를 입력해주세요!', description='15초만 기다려드릴거에요. 빠르게 골라주세요!')
        else:
            embed = discord.Embed(title=title, description=description)
        for i in range(len(itemList)):
            embed.add_field(name='> ' + str(i + 1), value=itemList[i]['itemName'])
        selection = await ctx.channel.send(embed=embed)

        try:
            def check(m):
                return ctx.channel.id == m.channel.id and ctx.message.author == m.author
            result = await bot.wait_for('message', check=check, timeout=15)
        except asyncio.TimeoutError:
            await selection.delete()
            await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
            return False
        except:
            await selection.delete()
            await result.delete()
            await ctx.channel.send('> 제대로 입력해주셔야해요! 다시 시도해주세요!')
            return False
        await selection.delete()
        await result.delete()
        itemId = itemList[int(result.content) - 1]['itemId']
    else:
        itemId = itemList[0]['itemId']
    return itemId

async def getSelectionFromSetItemIdList(bot, ctx, setItemIdList):
    await ctx.message.delete()

    if not len(setItemIdList):
        await ctx.channel.send('> 해당 세트를 찾을 수 없어요...\r\n> 세트 이름을 확인하고 다시 불러주세요!')
        return

    if len(setItemIdList) >= 2:
        embed = discord.Embed(title='알고싶은 세트옵션의 번호를 입력해주세요!', description='15초만 기다려드릴거에요. 빠르게 골라주세요!')
        for i in range(len(setItemIdList)):
            embed.add_field(name='> ' + str(i + 1), value=setItemIdList[i]['setItemName'])
        selection = await ctx.channel.send(embed=embed)

        try:
            def check(m):
                return ctx.channel.id == m.channel.id and ctx.message.author == m.author
            result = await bot.wait_for('message', check=check, timeout=15)
        except asyncio.TimeoutError:
            await selection.delete()
            await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
            return False
        else:
            await selection.delete()
            await result.delete()
            await ctx.channel.purge(limit=2)
            try:
                setItemId, setItemName = setItemIdList[int(result.content) - 1]['setItemId'], setItemIdList[int(result.content) - 1]['setItemName']
            except:
                await ctx.channel.send('> 제대로 입력해주셔야해요! 다시 시도해주세요!')
                return False
    else:
        setItemId, setItemName = setItemIdList[0]['setItemId'], setItemIdList[0]['setItemName']
    return setItemId, setItemName

# # # 계 산 # # #
def getSirocoItemInfo(chrEquipItemInfo, isBuff=False):
    sirocoInfo = {}

    ### 데이터 ###
    reverberation = {}

    intangible = {}
    intangibleType = ''

    unconscious = {}
    unconsciousType = ''

    illusion = {}
    illusionType = ''

    setCount = {
        '넥스'  : 0,
        '암살자': 0,
        '록시'  : 0,
        '수문장': 0,
        '로도스': 0
    }

    ### 딜러 옵션 or 버퍼 옵션 선택 ###
    dataType = 'explain' if not isBuff else 'buffExplain'

    ### 계산 ###
    for i in chrEquipItemInfo:
        try:
            for name in ['넥스', '암살자', '록시', '수문장', '로도스']:
                if name in i['upgradeInfo']['itemName']:
                    setCount[name] = setCount[name] + 1
        except: pass

        try:
            for j in i['sirocoInfo']['options']:
                if i['slotName'] == '무기':
                    if reverberation.get('1옵션') is None:
                        reverberation.update({'1옵션' : j[dataType]})
                    else:
                        reverberation.update({'2옵션': j[dataType]})

                elif i['slotName'] == '하의':
                    if intangible.get('1옵션') is None:
                        intangible.update({'1옵션' : j[dataType]})
                        intangibleType = i['upgradeInfo']['itemName']
                    else:
                        intangible.update({'2옵션': j[dataType]})
                        intangibleType = i['upgradeInfo']['itemName']

                elif i['slotName'] == '반지':
                    if unconscious.get('1옵션') is None:
                        unconscious.update({'1옵션' : j[dataType]})
                        unconsciousType = i['upgradeInfo']['itemName']
                    else:
                        unconscious.update({'2옵션': j[dataType]})
                        unconsciousType = i['upgradeInfo']['itemName']

                elif i['slotName'] == '보조장비':
                    if illusion.get('1옵션') is None:
                        illusion.update({'1옵션' : j[dataType]})
                        illusionType = i['upgradeInfo']['itemName']
                    else:
                        illusion.update({'2옵션': j[dataType]})
                        illusionType = i['upgradeInfo']['itemName']
        except: pass

    sirocoInfo['세트'] = setCount
    if len(reverberation) != 0: sirocoInfo['잔향'] = reverberation
    if len(intangible)    != 0: sirocoInfo[intangibleType] = intangible
    if len(unconscious)   != 0: sirocoInfo[unconsciousType] = unconscious
    if len(illusion)      != 0: sirocoInfo[illusionType] = illusion

    if len(reverberation) == 0 and len(intangible) == 0 and len(unconscious) == 0 and len(illusion) == 0:
        return None
    else:
        return sirocoInfo

def getFinalDamage(dmgInc, addDmgInc, criDmgInc, addCriDmgInc, addDmg, eleAddDmg, allDmgInc, adApInInc, strIntInc, element, skillDmgInc, continueDmg):
    damage = 1
    damage *= 1 + ((dmgInc + addDmgInc) / 100)          # 데미지 증가
    damage *= 1 + ((criDmgInc + addCriDmgInc) / 100)    # 크리티컬 데미지 증가
    damage *= 1 + ((addDmg + eleAddDmg) / 100)          # 추가데미지
    damage *= 1 + allDmgInc / 100                       # 모든 공격력 증가
    damage *= 1 + adApInInc / 100                       # 물리 마법 독립공격력 증가
    damage *= 1 + strIntInc / 250                       # 힘, 지능 증가
    damage *= 1 + ((element + 11) / 222)                # 속성 강화
    damage *= skillDmgInc                               # 스킬 데미지 증가
    damage *= 1 + continueDmg / 100                     # 지속 피해
    damage = int(damage)
    return damage

def getChrAllItemOptions(chrEquipData, chrAvatarData):
    # 장착한 장비 옵션
    chrEquipItem = chrEquipData[0]
    chrEquipItemIdList = [i['itemId'] for i in chrEquipItem]
    chrEquipItemInfoList = DNFAPI.getItemsDetail(chrEquipItemIdList)
    
    # 장착한 세트 옵션
    chrEquipSetItem = chrEquipData[1]
    chrEquipSetItemIdList = [i['setItemId'] for i in chrEquipSetItem]
    chrEquipSetItemInfoList = DNFAPI.getSetItemInfos(chrEquipSetItemIdList)
    chrEquipSetItemActiveSetNo = {}
    for i in chrEquipSetItem:
        chrEquipSetItemActiveSetNo.update( {i['setItemName'] : i['activeSetNo']} )

    # 모든 옵션은 이곳에 담겨져 있음
    allItemOption = []

    # 1. 기본 아이템 옵션
    # 2. 버퍼 전용 옵션
    for i in chrEquipItemInfoList:
        itemExplain = i.get('itemExplain')
        if itemExplain:
            allItemOption += itemExplain.split('\n')

        itemBuffExplain = i.get('itemBuff')
        if itemBuffExplain:
            allItemOption += itemBuffExplain['explain'].split('\n')
            reinforceSkill = itemBuffExplain.get('reinforceSkill')
            if reinforceSkill:
                for j in reinforceSkill:
                    for k in j['skills']:
                        text = k['name'] + ' 스킬Lv +' + str(k['value'])
                        allItemOption.append(text)

    # 3. 세트 옵션
    for i in chrEquipSetItemInfoList:
        for j in i['setItemOption']:
            if chrEquipSetItemActiveSetNo.get( i['setItemName'] ) >= j['optionNo']:
                try:
                    allItemOption += j['explain'].split('\n')
                except: pass
                allItemOption += j['itemBuff']['explain'].split('\n')
                reinforceSkill = j['itemBuff'].get('reinforceSkill')
                if reinforceSkill:
                    allItemOption += getSkillLevelingInfo(reinforceSkill)

    # 4. 칭호 옵션
    # 5. 연옥 변환 옵션
    # 6. 신화 전용 옵션
    for i in chrEquipItem:
        try:
            if i['slotName'] == '칭호':
                reinforceSkill = i['enchant']['reinforceSkill']
                allItemOption += getSkillLevelingInfo(reinforceSkill)
        except: pass

        try:
            transformInfo = i.get('transformInfo')
            allItemOption += transformInfo['explain'].split('\n')
            allItemOption += transformInfo['buffExplain'].split('\n')
        except: pass

        try:
            for j in i['mythologyInfo']['options']:
                allItemOption += j['buffExplain'].split('\n')
        except: pass

    # 8. 시로코 옵션
    sirocoInfo = getSirocoItemInfo(chrEquipItem, isBuff=True)
    if sirocoInfo is not None:
        ### 1세트 옵션 ###
        for k in sirocoInfo.keys():
            try:
                allItemOption.append(sirocoInfo[k]['1옵션'])
            except: pass

        ### 2세트 옵션 ###
        ## 잔향 ##
        if 3 in sirocoInfo['세트'].values():
            try:
                allItemOption.append(sirocoInfo['잔향']['2옵션'])
            except: pass

        ## 넥스 ##
        if  '무형 : 넥스의 잠식된 의복' in sirocoInfo.keys() and \
            '무의식 : 넥스의 몽환의 어둠' in sirocoInfo.keys():
            allItemOption.append(sirocoInfo['무형 : 넥스의 잠식된 의복']['2옵션'])

        if '무의식 : 넥스의 몽환의 어둠' in sirocoInfo.keys() and \
            '환영 : 넥스의 검은 기운' in sirocoInfo.keys():
            allItemOption.append(sirocoInfo['무의식 : 넥스의 몽환의 어둠']['2옵션'])
        if '환영 : 넥스의 검은 기운' in sirocoInfo.keys() and \
            '무형 : 넥스의 잠식된 의복' in sirocoInfo.keys():
            allItemOption.append(sirocoInfo['환영 : 넥스의 검은 기운']['2옵션'])

    # 9. 아바타 옵션
    for i in chrAvatarData['avatar']:
        try:
            allItemOption.append(i['optionAbility'])
        except: pass

    return allItemOption

def getApplyStatFromBuffEquip(chrBuffEquip):
    result = 0
    equip = chrBuffEquip['skill']['buff']['equipment']

    ### 퍼페티어 지능 N 증가 정규식 ###
    pp = re.compile('퍼페티어지능\+(?P<value>\d+)증가')

    # for i in equip:
    #     print(i)

    return result

# # # 편 리 # # #
def mergeString(*input):
    result= ''
    for i in input:
        result += i + ' '
    result = result.rstrip()
    return result

def getChrSkillLv(chrSkillStyle, skillId, isActive=True):
    skillType = 'active' if isActive else 'passive'
    for i in chrSkillStyle['skill']['style'][skillType]:
        if i['skillId'] == skillId:
            return i['level']
    return 0

def getChrSpecificStat(chrStatInfo, statName):
    for i in chrStatInfo['status']:
        if i['name'] == statName:
            return i['value']
    return 0

def getSkillValue(skillInfo, level):
    for i in skillInfo['levelInfo']['rows']:
        if i['level'] == level:
            return i['optionValue']
    return None

def getSkillLevelingInfo(reinforceSkill):
    result = {}
    for j in reinforceSkill:
        jobName = '모든 직업' if j['jobName'] == '공통' else j['jobName']

        ### 레벨 범위 레벨링일 경우 ###
        levelRange = j.get('levelRange')
        if levelRange is not None:
            for k in j['levelRange']:
                minLv, maxLv, value = k.values()
                text = str(minLv) + ' ~ ' + str(maxLv) + ' 레벨 모든 스킬 Lv +' + str(value)

                if result.get(jobName) is None:
                    result[jobName] = [text]
                else:
                    result[jobName].append(text)

        ### 단순 스킬 레벨링일 경우 ###
        skills = j.get('skills')
        if skills is not None:
            for k in skills:
                text = k['name'] + ' 스킬Lv +' + str(k['value'])

                if result.get(jobName) is None:
                    result[jobName] = [text]
                else:
                    result[jobName].append(text)
    return result

def getDailyReward():
    """
    확률  금액      누적
    1%  : 0         : 1%
    1%  : 100,000   : 2%
    4%  : 200,000   : 6%
    8%  : 300,000   : 14%
    16% : 400,000   : 30%
    20% : 500,000   : 50%
    20% : 600,000   : 70%
    16% : 700,000   : 86%
    8%  : 800,000   : 94%
    4%  : 900,000   : 98%
    1%  : 1,000,000 : 99%
    1%  : 2,000,000 : 100%
    """

    import random
    seed = int(random.random() * 100)
    if 0 <= seed < 1:       return 0
    elif 1 <= seed < 2:     return 100000
    elif 2 <= seed < 6:     return 200000
    elif 6 <= seed < 14:    return 300000
    elif 14 <= seed < 30:   return 400000
    elif 30 <= seed < 50:   return 500000
    elif 50 <= seed < 70:   return 600000
    elif 70 <= seed < 86:   return 700000
    elif 86 <= seed < 94:   return 800000
    elif 94 <= seed < 98:   return 900000
    elif 98 <= seed < 99:   return 1000000
    else:                   return 2000000

def getChicBotChannel(guild):
    result = []
    for ch in guild.text_channels:
        try:
            if '#시크봇' in ch.topic:
                result.append(ch)
        except: pass
    return result

def getVolatility(prev, now):
    if prev is None:
        return '데이터 없음'
    volatility = ((now / prev) - 1) * 100
    if volatility > 0:
        volatility = '▲ ' + str(format(volatility, '.2f')) + '%'
    elif volatility == 0:
        volatility = '- 0.00%'
    else:
        volatility = '▼ ' + str(format(volatility, '.2f')) + '%'
    return volatility
