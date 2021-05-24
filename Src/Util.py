import asyncio
import discord
import re

# # # 선 택 # # #
async def getSelectionFromChrIdList(bot, ctx, chrsInfo):
    await ctx.message.delete()

    if len(chrsInfo) == 0:
        await ctx.channel.send('> 해당 캐릭터를 찾을 수 없어요. 다시 한번 확인해주세요.')
        return None

    if len(chrsInfo) == 1:
        return chrsInfo[0]['server'], chrsInfo[0]['characterId'], chrsInfo[0]['characterName']

    # embed 생성
    embed = discord.Embed(title='원하는 캐릭터의 번호를 입력해주세요.',
                          description='15초 안에 입력하지 않으면 자동으로 취소되요.')
    for idx, chrInfo in enumerate(chrsInfo):
        embed.add_field(name=f"> {idx + 1}",
                        value=f"Lv.{chrInfo['level']} {chrInfo['characterName']}\n"
                              f"서버 : {chrInfo['server']}\n"
                              f"직업 : {chrInfo['jobGrowName']}")
    selection = await ctx.channel.send(embed=embed)

    try:
        def check(message):
            return ctx.channel.id == message.channel.id and ctx.message.author.id == message.author.id
        answer = await bot.wait_for('message', check=check, timeout=15)
        idx = int(answer.content) - 1
        result = chrsInfo[idx]['server'], chrsInfo[idx]['characterId'], chrsInfo[idx]['characterName']
        await answer.delete()
        await selection.delete()
        return result

    except asyncio.TimeoutError:
        await selection.edit(content='> 시간 끝! 더 고민해보고 다시 불러주세요.', embed=None)
        return False

    except:
        await answer.delete()
        await selection.edit(content='> 입력이 잘못됬어요. 다시 시도해주세요.', embed=None)
        return False

async def getItemIdFromItemsInfo(bot, ctx, itemsInfo,
                                 title=None, description=None, footer=None, skip=True):
    await ctx.message.delete()

    if len(itemsInfo) == 0:
        await ctx.channel.send('> 해당 장비를 찾을 수 없어요.\n'
                               '> 장비 이름을 확인하고 다시 불러주세요!')
        return None

    if len(itemsInfo) == 1 and skip:
        return itemsInfo[0]['itemId']

    # embed 생성
    if title is None or description is None:
        embed = discord.Embed(title='원하는 장비 아이템의 번호를 입력해주세요.',
                              description='15초 안에 입력하지 않으면 자동으로 취소되요.')
    else:
        embed = discord.Embed(title=title, description=description)
    
    # footer 설정
    if footer is not None: embed.set_footer(text=footer)

    # 선택지 설정
    for idx, itemInfo in enumerate(itemsInfo):
        embed.add_field(name=f"> {idx + 1}", value=itemInfo['itemName'])
    selection = await ctx.channel.send(embed=embed)

    try:
        def check(message):
            return ctx.channel.id == message.channel.id and ctx.author.id == message.author.id
        answer = await bot.wait_for('message', check=check, timeout=15)
        result = itemsInfo[int(answer.content) - 1]['itemId']
        await answer.delete()
        await selection.delete()
        return result

    except asyncio.TimeoutError:
        await selection.edit(content='> 시간 종료. 더 고민해보고 다시 불러주세요.', embed=None)
        return None

    except:
        await answer.delete()
        await selection.edit(content='> 입력이 잘못됬어요. 다시 시도해주세요.', embed=None)
        return None

async def getSetItemIdFromSetsInfo(bot, ctx, setsInfo,
                                   title=None, description=None, footer=None, skip=True):
    await ctx.message.delete()

    if len(setsInfo) == 0:
        await ctx.channel.send('> 해당 세트를 찾을 수 없어요...\n'
                               '> 세트 이름을 확인하고 다시 불러주세요!')
        return None

    if len(setsInfo == 1) and skip:
        return setsInfo[0]['setItemId'], setsInfo[0]['setItemName']

    # embed 생성
    if title is None or description is None:
        embed = discord.Embed(title='원하는 세트옵션의 번호를 입력해주세요.',
                              description='15초 안에 입력하지 않으면 자동으로 취소되요.')
    else:
        embed = discord.Embed(title=title, description=description)
        
    # footer 설정
    if footer is not None: embed.set_footer(text=footer)

    # 선택지 설정
    for idx, setInfo in enumerate(setsInfo):
        embed.add_field(name=f"> {idx + 1}", value=setsInfo['setItemName'])
    selection = await ctx.channel.send(embed=embed)

    try:
        def check(message):
            return ctx.channel.id == message.channel.id and ctx.author.id == message.author.id
        answer = await bot.wait_for('message', check=check, timeout=15)
        result = setsInfo[int(answer.content) - 1]['setItemId'], setsInfo[int(answer.content) - 1]['setItemName']
        await answer.delete()
        await selection.delete()
        return result

    except asyncio.TimeoutError:
        await selection.edit(content='> 시간 끝! 더 고민해보고 다시 불러주세요.', embed=None)
        return None

    except:
        await answer.delete()
        await selection.edit(content='> 입력이 잘못됬어요. 다시 시도해주세요.', embed=None)
        return None

# # # 계 산 # # #
def getFinalDamage(dmgInc, addDmgInc, criDmgInc, addCriDmgInc, addDmg, eleAddDmg,
                   allDmgInc, adApInInc, strIntInc, element, skillDmgInc, continueDmg):
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

def getApplyStatFromBuffEquip(chrBuffEquip):
    result = 0
    equip = chrBuffEquip['skill']['buff']['equipment']

    ### 퍼페티어 지능 N 증가 정규식 ###
    pp = re.compile('퍼페티어지능\+(?P<value>\d+)증가')

    # for i in equip:
    #     print(i)

    return result

# # # 편 리 # # #
def getChicBotChannel(guild):
    result = []
    for ch in guild.text_channels:
        try:
            if '#시크봇' in ch.topic:
                result.append(ch)
        except: continue
    return result

def getChrSkillLv(chrSkillStyle, skillId, isActive=True):
    skillType = 'active' if isActive else 'passive'
    for i in chrSkillStyle['skill']['style'][skillType]:
        if i['skillId'] == skillId:
            return i['level']
    return None

def getChrSpecificStat(chrStatInfo, statName):
    for i in chrStatInfo['status']:
        if i['itemName'] == statName:
            return i['value']
    return None

def getSkillValue(skillInfo, level):
    for i in skillInfo['levelInfo']['rows']:
        if i['level'] == level:
            return i['optionValue']
    return None

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

def getVolatility(prev, latest):
    if prev is None:
        return '데이터 없음'
    volatility = ((latest / prev) - 1) * 100
    if volatility > 0:
        volatility = '▲ ' + str(format(volatility, '.2f')) + '%'
    elif volatility == 0:
        volatility = '- 0.00%'
    else:
        volatility = '▼ ' + str(format(volatility, '.2f')) + '%'
    return volatility
