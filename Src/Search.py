import discord
from Database import Tool
from datetime import datetime
from Src import Util, DNFAPI

async def 등급(ctx):
    await ctx.message.delete()
    waiting = await ctx.channel.send('> 오늘의 아이템 등급을 읽어오고있어요...')

    itemIdList = ['8e0233bd504efc762b76a476d0e08de4', '52b3fac226cfa92cba9cffff516fb06e',
                  '7fae76b5a3fd513001a5d40716e1287f']

    MAX_OPTION = {
        '8e0233bd504efc762b76a476d0e08de4' : {
            '물리 방어력': 4475,
            '힘': 57,
            '지능': 37,
            '모든 속성 강화': 22
        },
        '52b3fac226cfa92cba9cffff516fb06e' : {
            '물리 방어력': 2983,
            '힘': 47,
            '지능': 47,
            '정신력': 52,
            '모든 속성 강화': 14
        },
        '7fae76b5a3fd513001a5d40716e1287f' : {
            '물리 공격력': 1113,
            '마법 공격력': 1348,
            '독립 공격력': 719,
            '지능': 78
        }
    }

    shopItemInfo = [DNFAPI.getShopItemInfo(i) for i in itemIdList]

    embed = discord.Embed(title='오늘의 아이템 등급을 알려드릴게요!')
    for i in shopItemInfo:
        value = i['itemGradeName'] + '(' + str(i['itemGradeValue']) + '%)\r\n'
        for j in i['itemStatus']:
            if j['itemName'] in MAX_OPTION[i['itemId']].keys():
                diff = j['value'] - MAX_OPTION[i['itemId']][j['itemName']]
                value += j['itemName'] + ' : ' + str(j['value']) + '(' + str(diff) + ')\r\n'
        embed.add_field(name='> ' + i['itemName'], value=value)

    if shopItemInfo[0]['itemGradeName'] == '최하급':
        footer = '오늘 하루는 절대 정가 금지!'
    elif shopItemInfo[0]['itemGradeName'] == '하급':
        footer = '아무리 그래도 하급은 아니죠...'
    elif shopItemInfo[0]['itemGradeName'] == '중급':
        footer = '중급...도 조금 그래요.'
    elif shopItemInfo[0]['itemGradeName'] == '상급':
        footer = '조금 아쉬운데, 급하다면 어쩔 수 없어요!'
    elif shopItemInfo[0]['itemGradeName'] == '최상급':
        footer = '오늘만을 기다려왔어요!!'
    else:
        footer = '오류'
    embed.set_footer(text=footer)

    await waiting.delete()
    await ctx.channel.send(embed=embed)

async def 캐릭터(bot, ctx, *input):
    if not input:
        await ctx.message.delete()
        await ctx.channel.send('> !캐릭터 <닉네임> 또는 !캐릭터 <서버> <닉네임> 의 형태로 적어야해요!')
        return

    if len(input) == 2:
        server = input[0]
        name   = input[1]
    else:
        server = '전체'
        name   = input[0]

    try:
        chrIdList = DNFAPI.getChrIdList(server, name)
        server, chrId, name = await Util.getSelectionFromChrIdList(bot, ctx, chrIdList)
    except:
        return False

    chrEquipItemInfo = DNFAPI.getChrEquipItems(server, chrId)
    chrEquipItemIds  = []
    for i in chrEquipItemInfo['equipment']:
        if i['slotName'] in ['칭호', '보조무기']: continue
        chrEquipItemIds.append(i['itemId'])
    chrEquipSetInfo = DNFAPI.getEquipActiveSet(chrEquipItemIds)

    infoSwitch = True
    embed = getChrInfoEmbed(name, chrEquipSetInfo, chrEquipItemInfo)
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('▶️')
    
    while True:
        try:
            def check(reaction, user):
                return (str(reaction) == '◀️' or str(reaction) == '▶️') \
                       and user == ctx.author and reaction.message.id == msg.id
            reaction, user = await bot.wait_for('reaction_add', check=check)

            # 아바타 정보
            if infoSwitch and str(reaction) == '▶️':
                avatar = DNFAPI.getChrEquipAvatar(server, chrId)
                embed = getChrAvatarInfoEmbed(name, avatar)
                embed.set_image(url=DNFAPI.getChrImageUrl(server, chrId))
                await msg.edit(embed=embed)
                await msg.clear_reactions()
                await msg.add_reaction('◀️')
                infoSwitch = not infoSwitch

            # 캐릭터 정보
            elif not infoSwitch and str(reaction) == '◀️':
                embed = getChrInfoEmbed(name, chrEquipSetInfo, chrEquipItemInfo)
                await msg.edit(embed=embed)
                await msg.clear_reactions()
                await msg.add_reaction('▶️')
                infoSwitch = not infoSwitch
        except: pass

async def 시세(ctx, *input):
    await ctx.message.delete()
    waiting = await ctx.channel.send('> 아이템 시세 정보를 불러오고 있어요...')

    item = DNFAPI.getMostSimilarItem(' '.join(input))
    if item is None:
        await waiting.delete()
        await ctx.channel.send('> 해당 아이템의 판매 정보를 얻어오지 못했어요.')
        return
    itemName = item['itemName']

    embed = discord.Embed(title=f"'{itemName}' 시세를 알려드릴게요")
    if '카드' in itemName:
        auction = DNFAPI.getItemAuction(itemName)
        upgrades = [int(i['upgrade']) for i in auction]
        upgrades = list(set(upgrades))
        upgrades.sort()

        for upgrade in upgrades:
            p, count = 0, 0
            for i in auction:
                if upgrade == int(i['upgrade']):
                    p += i['price']
                    count += i['count']
            price = p // count

            Tool.updateAuctionPrice(f"{itemName} +{upgrade}", price)

            prev, latest = Tool.getPrevPrice(f"{itemName} +{upgrade}"), Tool.getLatestPrice(f"{itemName} +{upgrade}")
            embed.add_field(name='> +' + str(upgrade) + ' 평균 가격', value=format(latest['price'], ',') + '골드')
            embed.add_field(name='> 최근 판매량', value=format(count, ',') + '개')
            if prev is None:
                embed.add_field(name='> 가격 변동률', value='데이터 없음')
            else:
                embed.add_field(name='> 가격 변동률', value=Util.getVolatility(prev['price'], latest['price']) + ' (' + prev['date'].strftime('%Y-%m-%d') + ')')
    else:
        auction = DNFAPI.getItemAuction(itemName)

        p, count = 0, 0
        for i in auction:
            p += i['price']
            count += i['count']
        price = p // count

        Tool.updateAuctionPrice(itemName, price)

        prev, latest = Tool.getPrevPrice(itemName), Tool.getLatestPrice(itemName)
        embed.add_field(name='> 평균 가격', value=format(latest['price'], ',') + '골드')
        embed.add_field(name='> 최근 판매량', value=format(count, ',') + '개')
        if prev is None:
            embed.add_field(name='> 가격 변동률', value='데이터 없음')
        else:
            embed.add_field(name='> 가격 변동률', value=Util.getVolatility(prev['price'], latest['price']) + '(' + prev['date'].strftime('%Y-%m-%d') + ')')

    embed.set_footer(text=auction[-1]['soldDate'] + ' 부터 ' + auction[0]['soldDate'] + ' 까지 집계된 자료예요.')
    embed.set_thumbnail(url=DNFAPI.getItemImageUrl(auction[0]['itemId']))
    await waiting.delete()
    await ctx.channel.send(embed=embed)

async def 장비(bot, ctx, *input):
    name = Util.mergeString(*input)
    if len(name) < 1:
        await ctx.message.delete()
        await ctx.channel.send('> !장비 <장비템이름> 의 형태로 적어야해요!')
        return

    try:
        itemIdList = DNFAPI.getItem(name)
        itemId = await Util.getSelectionFromItemIdList(bot, ctx, itemIdList)
        if itemId is False: return
    except: return
    itemDetailInfo = DNFAPI.getItemDetail(itemId)

    infoSwitch = True
    embed = getItemOptionEmbed(itemDetailInfo)
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('▶️')

    while True:
        try:
            def check(_reaction, _user):
                return str(_reaction) in ['◀️', '▶️'] and _user == ctx.author and _reaction.message.id == msg.id
            reaction, user = await bot.wait_for('reaction_add', check=check)

            # 버퍼 옵션
            if infoSwitch and str(reaction) == '▶️':
                await msg.edit(embed=getItemBuffOptionEmbed(itemDetailInfo))
                await msg.clear_reactions()
                await msg.add_reaction('◀️')
                infoSwitch = not infoSwitch

            # 딜러 옵션
            elif not infoSwitch and str(reaction) == '◀️':
                await msg.edit(embed=getItemOptionEmbed(itemDetailInfo))
                await msg.clear_reactions()
                await msg.add_reaction('▶️')
                infoSwitch = not infoSwitch
        except: pass

async def 세트(bot, ctx, *input):
    name = Util.mergeString(*input)

    if len(name) < 1:
        await ctx.message.delete()
        await ctx.channel.send('> !세트 <세트옵션이름> 의 형태로 적어야해요!')
        return

    try:
        setItemIdList = DNFAPI.getSetItemIdList(name)
        setItemId, name = await Util.getSelectionFromSetItemIdList(bot, ctx, setItemIdList)
    except:
        return
    setItemInfo = DNFAPI.getSetItemInfo(setItemId)

    infoSwitch = True
    embed = getSetItemOptionEmbed(setItemInfo)
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('▶️')

    while True:
        try:
            def check(_reaction, _user):
                return str(_reaction) == ['◀️', '▶️'] and _user == ctx.author and _reaction.message.id == msg.id
            reaction, user = await bot.wait_for('reaction_add', check=check)

            # 버퍼 옵션
            if infoSwitch and str(reaction) == '▶️':
                await msg.edit(embed=getSetItemBuffOptionEmbed(setItemInfo))
                await msg.clear_reactions()
                await msg.add_reaction('◀️')
                infoSwitch = not infoSwitch

            # 딜러 옵션
            elif not infoSwitch and str(reaction) == '◀️':
                await msg.edit(embed=getSetItemOptionEmbed(setItemInfo))
                await msg.clear_reactions()
                await msg.add_reaction('▶️')
                infoSwitch = not infoSwitch
        except: pass

async def 에픽(bot, ctx, *input):
    if not input:
        await ctx.message.delete()
        await ctx.channel.send('> !에픽 <닉네임> 또는 !에픽 <서버> <닉네임> 의 형태로 적어야해요!')
        return

    if len(input) == 2:
        server = input[0]
        name   = input[1]
    else:
        server = '전체'
        name   = input[0]

    try:
        chrIdList = DNFAPI.getChrIdList(server, name)
        server, chrId, name = await Util.getSelectionFromChrIdList(bot, ctx, chrIdList)
    except: return False

    waiting = await ctx.channel.send(f'> {name}님이 획득한 에픽을 확인 중이예요...')
    timeline = DNFAPI.getChrTimeLine(server, chrId, 505, 513)

    # 획득한 에픽 갯수
    gainEpicCount = len(timeline)
    if gainEpicCount == 0:
        await waiting.delete()
        await ctx.channel.send(f'> {name}님은 이번 달 획득한 에픽이 없어요.. ㅠㅠ')
        return

    # 에픽을 가장 많이 획득한 채널
    channels = {}
    for i in timeline:
        if i['code'] == 505:
            channels.setdefault(f"ch{i['data']['channelNo']}.{i['data']['channelName']}", 0)
            channels[f"ch{i['data']['channelNo']}.{i['data']['channelName']}"] += 1

    if channels == {}:
        luckyChannel = '없음'
    else:
        luckyChannel = sorted(channels.items(), key=lambda x: x[1], reverse=True)[0][0]
    Tool.updateEpicRank(server, name, gainEpicCount, luckyChannel)
    await waiting.delete()

    page = 0
    embed = getGainEpicEmbed(timeline, name, luckyChannel, page)
    embed.set_footer(text=f'{(gainEpicCount - 1) // 15 + 1}쪽 중 1쪽')
    msg = await ctx.channel.send(embed=embed)

    if gainEpicCount > 15:
        await msg.add_reaction('▶️')
    while gainEpicCount > 15:
        try:
            def check(_reaction, _user):
                return str(_reaction) in ['◀️', '▶️'] and _user == ctx.author and _reaction.message.id == msg.id
            reaction, user = await bot.wait_for('reaction_add', check=check)

            if str(reaction) == '◀️' and page > 0:
                page -= 1
            if str(reaction) == '▶️' and page < (gainEpicCount - 1) // 15:
                page += 1

            embed = getGainEpicEmbed(timeline, name, luckyChannel, page)
            embed.set_footer(text=f'{(gainEpicCount - 1) // 15 + 1}쪽 중 {page + 1}쪽')
            await msg.edit(embed=embed)
            await msg.clear_reactions()

            if page > 0:
                await msg.add_reaction('◀️')
            if page < (gainEpicCount - 1) // 15:
                await msg.add_reaction('▶️')
        except:
            await msg.delete()
            await ctx.channel.send('> 오류가 발생했습니다.')
            return

async def 에픽랭킹(bot, ctx):
    await ctx.message.delete()
    waiting = await ctx.channel.send('> 기린 랭킹을 불러오는 중이예요...')

    rank = Tool.getMonthlyEpicRank()
    rank = list(sorted(rank, key=lambda x: x['count'], reverse=True))
    await waiting.delete()

    if not rank:
        today = datetime.today()
        embed = discord.Embed(title=f'{today.year}년 {today.month}월 기린 랭킹을 알려드릴게요!',
                              description='> 랭킹 데이터가 없어요.\r\n'
                                          '> `!에픽` 명령어를 사용해서 랭킹에 등록해보세요!')
        await ctx.channel.send(embed=embed)
        return

    page = 0
    embed = getEpicRankEmbed(rank, page)
    embed.set_footer(text=f'{(len(rank) - 1) // 15 + 1}쪽 중 {page + 1}쪽')
    msg = await ctx.channel.send(embed=embed)

    if len(rank) > 15:
        await msg.add_reaction('▶️')
    while len(rank) > 15:
        try:
            def check(_reaction, _user):
                return str(_reaction) in ['◀️', '▶️'] and _user == ctx.author and _reaction.message.id == msg.id
            reaction, user = await bot.wait_for('reaction_add', check=check)

            if str(reaction) == '◀️' and page > 0:
                page -= 1
            if str(reaction) == '▶️' and page < (len(rank) - 1) // 15:
                page += 1

            embed = getEpicRankEmbed(rank, page)
            embed.set_footer(text=f'{(len(rank) - 1) // 15 + 1}쪽 중 {page + 1}쪽')
            await msg.edit(embed=embed)
            await msg.clear_reactions()

            if page > 0:
                await msg.add_reaction('◀️')
            if page < (len(rank) - 1) // 15:
                await msg.add_reaction('▶️')
        except:
            await msg.delete()
            await ctx.channel.send('> 오류가 발생했습니다.')
            return

def getChrInfoEmbed(name, chrEquipSetInfo, chrEquipItemInfo):
    embed = discord.Embed(title=name + '님의 캐릭터 정보를 알려드릴게요.')

    ### 장착중인 세트 ###
    try:
        for i in chrEquipSetInfo['setItemInfo']:
            try:
                setInfo += i['setItemName'] + '(' + str(i['activeSetNo']) + ')\r\n'
            except:
                setInfo = i['setItemName'] + '(' + str(i['activeSetNo']) + ')\r\n'
        embed.add_field(name='> 장착중인 세트', value=setInfo, inline=False)
    except: pass

    ### 장비 옵션 ###
    for i in chrEquipItemInfo['equipment']:
        if i['slotName'] in ['칭호', '보조무기']: continue

        text = ''

        ### 강화, 재련 수치 ###
        if i['reinforce'] != 0:
            text += '+' + str(i['reinforce'])
        if i['refine'] != 0:
            text += '(' + str(i['refine']) + ')'
        text += ' ' + i['itemName'] + '\r\n'

        ### 마법부여 ###
        try:
            for j in i['enchant']['status']:
                text += j['itemName'] + ' +' + str(j['value']) + '\r\n'
        except: pass

        embed.add_field(name='> ' + i['slotName'], value=text)
    return embed

def getChrAvatarInfoEmbed(name, avatar):
    embed = discord.Embed(title=name + '님의 아바타 정보를 알려드릴게요.')
    for i in avatar['avatar']:
        if i['slotName'] == '오라 아바타': continue
        value = i['itemName'] + '\r\n'
        if i['clone']['itemName'] is not None:
            value += i['clone']['itemName']
        embed.add_field(name='> ' + i['slotName'], value=value)
    embed.set_footer(text='클론하고 있는 아바타가 있는 경우 해당 아바타도 표시해요.')
    return embed

def getItemOptionEmbed(itemDetailInfo):
    embed = discord.Embed(title=itemDetailInfo['itemName'],
                          description=str(itemDetailInfo['itemAvailableLevel']) + 'Lv ' + itemDetailInfo['itemRarity'] + ' ' + itemDetailInfo['itemTypeDetail'])
    # 스탯
    itemStatInfo = DNFAPI.getItemStatInfo(itemDetailInfo['itemStatus'])
    embed.add_field(name='> 스탯', value=itemStatInfo, inline=False)

    # 시로코 옵션
    try:
        sirocoInfo = ''
        for i in itemDetailInfo['sirocoInfo']['options']:
            #buffExplainDetail = i['buffExplainDetail'].replace('\n\n', '\n')
            #sirocoInfo += f"{i['explainDetail']}\n{buffExplainDetail}\n"
            sirocoInfo += f"{i['explainDetail']}\n"
        embed.add_field(name='> 시로코 옵션', value=sirocoInfo, inline=False)
    except: pass

    # 스킬 레벨
    try:
        itemSkillLvInfo = DNFAPI.getItemSkillLvInfo(itemDetailInfo['itemReinforceSkill'][0]['jobName'],
                                                    itemDetailInfo['itemReinforceSkill'][0]['levelRange'])
        embed.add_field(name='> 스킬', value=itemSkillLvInfo)
    except: pass

    # 기본 옵션
    if itemDetailInfo['itemExplainDetail'] != '':
        embed.add_field(name='> 옵션', value=itemDetailInfo['itemExplainDetail'], inline=False)

    # 변환 옵션
    try:
        itemTransformInfo = itemDetailInfo['transformInfo']['explain']
        embed.add_field(name='> 변환 옵션', value=itemTransformInfo, inline=False)
    except: pass

    # 신화옵션
    try:
        itemMythicInfo = DNFAPI.getItemMythicInfo(itemDetailInfo['mythologyInfo']['options'])
        embed.add_field(name='> 신화 전용 옵션', value=itemMythicInfo, inline=False)
    except: pass

    # 플레이버 텍스트
    try:
        itemFlavorText = itemDetailInfo['itemFlavorText']
        embed.set_footer(text=itemFlavorText)
    except: pass

    # 아이콘
    icon = DNFAPI.getItemImageUrl(itemDetailInfo['itemId'])
    embed.set_thumbnail(url=icon)

    return embed

def getItemBuffOptionEmbed(itemDetailInfo):
    embed = discord.Embed(title=itemDetailInfo['itemName'],
                          description=str(itemDetailInfo['itemAvailableLevel']) + 'Lv ' + itemDetailInfo['itemRarity'] + ' ' + itemDetailInfo['itemTypeDetail'])

    # 스탯
    statInfo = DNFAPI.getItemStatInfo(itemDetailInfo['itemStatus'])
    embed.add_field(name='> 스탯', value=statInfo, inline=False)

    # 시로코 옵션
    try:
        sirocoInfo = ''
        for i in itemDetailInfo['sirocoInfo']['options']:
            buffExplainDetail = i['buffExplainDetail'].replace('\n\n', '\n')
            sirocoInfo += f"{buffExplainDetail}\n"
        embed.add_field(name='> 시로코 옵션', value=sirocoInfo, inline=False)
    except: pass

    # 버프 스킬 레벨 옵션
    try:
        buffLvInfo = Util.getSkillLevelingInfo(itemDetailInfo['itemBuff']['reinforceSkill'])
        buffLvInfoValue = ''
        for key in buffLvInfo.keys():
            if key != '모든 직업':
                buffLvInfoValue += key + '\r\n'
            for lv in buffLvInfo[key]:
                if key == '모든 직업':
                    buffLvInfoValue += key + ' ' + lv + '\r\n'
                else:
                    buffLvInfoValue += lv + '\r\n'

        # 버프 옵션
        buffInfo = itemDetailInfo['itemBuff']['explain']
        embed.add_field(name='> 버퍼 전용 옵션', value=buffLvInfoValue + buffInfo, inline=False)
    except: pass

    # 신화 옵션
    try:
        mythicInfo = DNFAPI.getItemMythicInfo(itemDetailInfo['mythologyInfo']['options'], buff=True)
        embed.add_field(name='> 신화 전용 옵션', value=mythicInfo)
    except: pass

    # 플레이버 텍스트
    embed.set_footer(text=itemDetailInfo['itemFlavorText'])

    # 아이콘
    icon = DNFAPI.getItemImageUrl(itemDetailInfo['itemId'])
    embed.set_thumbnail(url=icon)

    return embed

def getSetItemOptionEmbed(setItemInfo):
    embed = discord.Embed(title=setItemInfo['setItemName'] + '의 정보를 알려드릴게요.')
    for setItem in setItemInfo['setItems']:
        embed.add_field(name='> ' + setItem['itemRarity'] + ' ' + setItem['slotName'], value=setItem['itemName'])
    for option in setItemInfo['setItemOption']:
        value = ''
        try:
            for status in option['status']:
                value += status['itemName'] + ' ' + status['value'] + '\r\n'
        except: pass
        embed.add_field(name='> ' + str(option['optionNo']) + '세트 옵션', value=value + option['explain'])
    embed.set_thumbnail(url=DNFAPI.getItemImageUrl(setItemInfo['setItems'][0]['itemId']))
    return embed

def getSetItemBuffOptionEmbed(setItemInfo):
    embed = discord.Embed(title=setItemInfo['setItemName'] + '의 정보를 알려드릴게요.')
    for setItem in setItemInfo['setItems']:
        embed.add_field(name='> ' + setItem['itemRarity'] + ' ' + setItem['slotName'], value=setItem['itemName'])
    for option in setItemInfo['setItemOption']:
        value = ''
        try:
            skill = Util.getSkillLevelingInfo(option['itemBuff']['reinforceSkill'])
            for key in skill.keys():
                if key != '모든 직업':
                    value += key + '\r\n'
                for lv in skill[key]:
                    if key == '모든 직업':
                        value += key + ' ' + lv + '\r\n'
                    else:
                        value += lv + '\r\n'
        except: pass
        value += option['itemBuff']['explain']
        embed.add_field(name='> ' + str(option['optionNo']) + '세트 옵션', value=value)
    embed.set_thumbnail(url=DNFAPI.getItemImageUrl(setItemInfo['setItems'][0]['itemId']))
    return embed

def getGainEpicEmbed(timeline, name, luckyChannel, page):
    if luckyChannel == '없음':
        embed = discord.Embed(title=f'{name} 님은 이번 달에 {len(timeline)}개의 에픽을 획득했어요.')
    else:
        embed = discord.Embed(title=f'{name} 님은 이번 달에 {len(timeline)}개의 에픽을 획득했어요.',
                              description=f'`{luckyChannel}`에서 에픽을 가장 많이 획득했어요!')
    _timeline = timeline[page * 15:page * 15 + 15]
    for i in _timeline:
        if i['code'] == 505:
            embed.add_field(name=f"> {i['date'][:10]}\r\nch{i['data']['channelNo']}.{i['data']['channelName']}",
                            value=i['data']['itemName'])
        elif i['code'] == 513:
            embed.add_field(name=f"> {i['date'][:10]}\r\n{i['data']['dungeonName']}",
                            value=i['data']['itemName'])
    return embed

def getEpicRankEmbed(rank, page):
    rank = rank[page * 15:page * 15 + 15]
    today = datetime.today()
    embed = discord.Embed(title=f'{today.year}년 {today.month}월 기린 랭킹을 알려드릴게요!',
                          description='기린들이 어디서 에픽을 많이 먹었는지도 알려드릴게요.')
    for index, r in enumerate(rank):
        embed.add_field(name=f'> {page * 15 + index + 1}등\r\n'
                             f"> {r['server']} {r['itemName']}",
                        value=f"{r['channel']}\r\n에픽 {r['count']}개 획득!")
    embed.set_footer(text=f'{(len(rank) - 1) // 15 + 1}쪽 중 {page + 1}쪽')
    return embed

# async def 버프력(bot, ctx, itemName, server='전체'):
#     if itemName == 'None':
#         await ctx.message.delete()
#         await ctx.channel.send('> !버프력 <닉네임> 의 형태로 적어야해요!')
#         return
#
#     # 검색
#     try:
#         chrIdList = dnfAPI.getChrIdList(server, itemName)
#         server, chrId, itemName = await util.getSelectionFromChrIdList(bot, ctx, chrIdList)
#     except: return False
#
#     ### 계산에 필요한 데이터 불러오기 ###
#     chrStatInfo     = dnfAPI.getChrStatInfo(server, chrId)
#     chrSkillStyle   = dnfAPI.getChrSkillStyle(server, chrId)
#     equip    = dnfAPI.getChrEquipItems(server, chrId)
#     avatar   = dnfAPI.getChrEquipAvatar(server, chrId)
#     chrBuffEquip    = dnfAPI.getChrBuffEquip(server, chrId)
#     allItemOption   = util.getAllItemOptions(equip, avatar)
#
#     util.getApplyStatFromBuffEquip(chrBuffEquip)
#
#     ### 스킬 정보 불러오기 ###
#     ACTIVE_BUFF2_INFO = dnfAPI.getSkillInfo('3909d0b188e9c95311399f776e331da5', '56fca6cff74d828e92301a40cd2148b9') # 1각 액티브
#     ACTIVE_BUFF3_INFO = dnfAPI.getSkillInfo('3909d0b188e9c95311399f776e331da5', 'caef38e23a8ae551466f8a8eb039df22') # 진각 액티브
#     PASSIVE_BUFF_INFO = dnfAPI.getSkillInfo('3909d0b188e9c95311399f776e331da5', '0dbdeaf846356f8b9380f8fbb8e97377') # 1각 패시브
#
#     ### 캐릭터 스킬 레벨 ###
#     chrApplyStat    = util.getChrSpecificStat(chrStatInfo, '지능')
#     chr48LvSkillLv  = util.getChrSkillLv(chrSkillStyle, '0dbdeaf846356f8b9380f8fbb8e97377', False)
#     chr50LvSkillLv  = util.getChrSkillLv(chrSkillStyle, '56fca6cff74d828e92301a40cd2148b9')
#     chr100LvSkillLv = util.getChrSkillLv(chrSkillStyle, 'caef38e23a8ae551466f8a8eb039df22')
#
#     ### 변수 선언 ###
#     ACTIVE_BUFF1_SKILL_LV    = 0 # 30레벨 버프 스킬 레벨
#     ACTIVE_BUFF2_SKILL_LV    = 0 # 50레벨 버프 스킬 레벨
#     ACTIVE_BUFF3_SKILL_LV    = 0 # 100레벨 버프 스킬 레벨
#     PASSIVE_BUFF_SKILL_LV    = 0 # 48레벨 패시브 버프 스킬 레벨
#     ACTIVE_BUFF1_SKILL_STAT  = 0 # 30레벨 버프 스킬 힘, 지능 퍼센트 증가량
#     ACTIVE_BUFF2_SKILL_STAT1 = 0 # 50Lv 액티브 스킬 힘, 지능 증가량
#     ACTIVE_BUFF2_SKILL_STAT2 = 0 # 50Lv 액티브 스킬 힘, 지능 퍼센트 증가량
#
#     ForbiddenCurseLv = 0 # 금단의 저주
#     MarionetteLv     = 0 # 마리오네트
#     smallDevilLv     = 0 # 소악마
#
#     ### 정규식 ###
#     ACTIVE_BUFF1_SKILL_LV_RE    = re.compile('30Lv버프스킬레벨\+(?P<value>\d+)')
#     ACTIVE_BUFF2_SKILL_LV_RE    = re.compile('50Lv액티브스킬레벨\+(?P<value>\d+)')
#     ACTIVE_BUFF2_SKILL_STAT1_RE = re.compile('50Lv액티브스킬힘,지능증가량(?P<value>\d+)증가')
#     ACTIVE_BUFF2_SKILL_STAT2_RE = re.compile('50Lv액티브스킬힘,지능증가량(?P<value>\d+)%증가')
#     INC_SKILL_LV1_RE            = re.compile('모든직업(?P<value1>\d+)레벨모든스킬Lv\+(?P<value2>\d+)')
#     INC_SKILL_LV2_RE            = re.compile('모든직업(?P<value1>\d+)~(?P<value2>\d+)레벨모든스킬Lv\+(?P<value3>\d+)')
#
#     ForbiddenCurse_RE = re.compile('금단의저주스킬Lv\+(?P<value>\d+)')
#     MarionetteLv_RE   = re.compile('마리오네트스킬Lv\+(?P<value>\d+)')
#     smallDevilLv_RE   = re.compile('소악마스킬Lv\+(?P<value>\d+)')
#
#     ### 계산 ###
#     for option in allItemOption:
#         try:
#             option = option.replace(' ', '')
#         except: pass
#
#         try:
#             ### 30 레벨 스킬 레벨 증가 ###
#             result = ACTIVE_BUFF1_SKILL_LV_RE.search(option)
#             ACTIVE_BUFF1_SKILL_LV += int(result.group('value'))
#         except: pass
#
#         try:
#             ### 50 레벨 스킬 레벨 증가 ###
#             result = ACTIVE_BUFF2_SKILL_LV_RE.search(option)
#             ACTIVE_BUFF2_SKILL_LV += int(result.group('value'))
#         except: pass
#
#         try:
#             ### 50 레벨 스킬 힘, 지능 증가량1 ###
#             result = ACTIVE_BUFF2_SKILL_STAT1_RE.search(option)
#             ACTIVE_BUFF2_SKILL_STAT1 += int(result.group('value'))
#         except: pass
#
#         try:
#             ### 50 레벨 스킬 힘, 지능 증가량2 ###
#             result = ACTIVE_BUFF2_SKILL_STAT2_RE.search(option)
#             ACTIVE_BUFF2_SKILL_STAT2 += int(result.group('value'))
#         except: pass
#
#         try:
#             ### 모든 직업 N 레벨 스킬 레벨 증가 ###
#             result  = INC_SKILL_LV1_RE.search(option)
#             value   = int(result.group('value1'))
#             skillLv = int(result.group('value2'))
#             if value == 30: ACTIVE_BUFF1_SKILL_LV += skillLv
#             if value == 48: PASSIVE_BUFF_SKILL_LV += skillLv
#             if value == 50: ACTIVE_BUFF2_SKILL_LV += skillLv
#             if value == 100: ACTIVE_BUFF3_SKILL_LV += skillLv
#         except: pass
#
#         try:
#             ### 모든 직업 N ~ N 레벨 스킬 레벨 증가 ###
#             result = INC_SKILL_LV2_RE.search(option)
#             startLv = int(result.group('value1'))
#             endLv   = int(result.group('value2'))
#             skillLv = int(result.group('value3'))
#             if startLv <= 30 <= endLv: ACTIVE_BUFF1_SKILL_LV += skillLv
#             if startLv <= 48 <= endLv: PASSIVE_BUFF_SKILL_LV += skillLv
#             if startLv <= 50 <= endLv: ACTIVE_BUFF2_SKILL_LV += skillLv
#             if startLv <= 100 <= endLv: ACTIVE_BUFF3_SKILL_LV += skillLv
#         except: pass
#
#         ### 헤카테 ###
#         try:
#             # 금단의 저주
#             result = ForbiddenCurse_RE.search(option)
#             ForbiddenCurseLv += int(result.group('value'))
#         except: pass
#
#         try:
#             # 마리오네트
#             result = MarionetteLv_RE.search(option)
#             MarionetteLv += int(result.group('value'))
#         except: pass
#
#         try:
#             # 소악마
#             result = smallDevilLv_RE.search(option)
#             smallDevilLv += int(result.group('value'))
#         except: pass
#
#     # 탈리스만 선택 신발 :: 30Lv 버프 스킬 힘, 지능 증가량 6% 추가 증가
#     for i in chrBuffEquip['skill']['buff']['equipment']:
#         if i['itemName'] == '탈리스만 선택':
#             ACTIVE_BUFF1_SKILL_STAT += 6
#             break
#
#     ### 금단의 저주로 오르는 스탯 ###
#     values = chrBuffEquip['skill']['buff']['skillInfo']['option']['values'][4:-1]
#     ACTIVE_BUFF1_AD  = int((1 + chrApplyStat / 665) * int(values[0]) * (1 + ACTIVE_BUFF1_SKILL_STAT / 100))
#     ACTIVE_BUFF1_AP  = int((1 + chrApplyStat / 665) * int(values[1]) * (1 + ACTIVE_BUFF1_SKILL_STAT / 100))
#     ACTIVE_BUFF1_ID  = int((1 + chrApplyStat / 665) * int(values[2]) * (1 + ACTIVE_BUFF1_SKILL_STAT / 100))
#     ACTIVE_BUFF1_STR = int((1 + chrApplyStat / 665) * int(values[3]) * (1 + ACTIVE_BUFF1_SKILL_STAT / 100))
#     # ACTIVE_BUFF1_INT = int((1 + chrApplyStat / 665) * int(values[4]) * (1 + ACTIVE_BUFF1_SKILL_STAT / 100))
#
#     ### 마리오네트로 오르는 스탯 ###
#     ACTIVE_BUFF2_STAT = util.getSkillValue(ACTIVE_BUFF2_INFO, chr50LvSkillLv + ACTIVE_BUFF2_SKILL_LV + MarionetteLv + 1).get('value2')
#     ACTIVE_BUFF2_STAT += ACTIVE_BUFF2_SKILL_STAT1
#     ACTIVE_BUFF2_STAT *= 1 + ACTIVE_BUFF2_SKILL_STAT2 / 100
#     ACTIVE_BUFF2_STAT *= 1 + chrApplyStat / 750
#     ACTIVE_BUFF2_STAT = int(ACTIVE_BUFF2_STAT)
#
#     ### 종막극으로 오르는 스탯 ###
#     ACTIVE_BUFF3_STAT = util.getSkillValue(ACTIVE_BUFF3_INFO, chr100LvSkillLv + ACTIVE_BUFF3_SKILL_LV).get('value8')
#     ACTIVE_BUFF3_STAT = ACTIVE_BUFF2_STAT * (ACTIVE_BUFF3_STAT / 100)
#     ACTIVE_BUFF3_STAT = int(ACTIVE_BUFF3_STAT)
#
#     ### 소악마로 오르는 스탯 ###
#     PASSIVE_BUFF_STAT = util.getSkillValue(PASSIVE_BUFF_INFO, chr48LvSkillLv + PASSIVE_BUFF_SKILL_LV + smallDevilLv).get('value3')
#
#     ### 총 버프력 ###
#     # TOTAL1 = (1 + ((15000 + ACTIVE_BUFF1_STR + ACTIVE_BUFF2_STAT + ACTIVE_BUFF3_STAT + PASSIVE_BUFF_STAT) / 250)) *\
#     #         ( 2650 + ((ACTIVE_BUFF1_AD + ACTIVE_BUFF1_AP + ACTIVE_BUFF1_ID) / 3) )
#     # TOTAL1 = int(TOTAL1 / 10)
#     #
#     # TOTAL2 = (1 + ((15000 + ACTIVE_BUFF1_STR * 1.25 + ACTIVE_BUFF2_STAT + ACTIVE_BUFF3_STAT + PASSIVE_BUFF_STAT) / 250)) *\
#     #         ( 2650 + ((ACTIVE_BUFF1_AD * 1.25 + ACTIVE_BUFF1_AP * 1.25 + ACTIVE_BUFF1_ID * 1.25) / 3) )
#     # TOTAL2 = int(TOTAL2 / 10)
#
#     TOTAL = (1 + ((15000 + ACTIVE_BUFF1_STR * 1.25 * 1.15 + ACTIVE_BUFF2_STAT + ACTIVE_BUFF3_STAT + PASSIVE_BUFF_STAT) / 250)) *\
#             ( 2650 + ((ACTIVE_BUFF1_AD * 1.25 * 1.15 + ACTIVE_BUFF1_AP * 1.25 * 1.15 + ACTIVE_BUFF1_ID * 1.25 * 1.15) / 3) )
#     TOTAL = int(TOTAL / 10)
#
#     ### 출력 ###
#     embed = discord.Embed(title=itemName + '님의 버프력을 알려드릴게요!')
#     embed.add_field(itemName='> 금단의 저주(기본)',
#                     value='물리 공격력 : ' + format(ACTIVE_BUFF1_AD, ',') + '\r\n' +
#                           '마법 공격력 : ' + format(ACTIVE_BUFF1_AP, ',') + '\r\n' +
#                           '독립 공격력 : ' + format(ACTIVE_BUFF1_ID, ',') + '\r\n' +
#                           '힘, 지능 : '    + format(ACTIVE_BUFF1_STR, ',') + '\r\n')
#     embed.add_field(itemName='> 금단의 저주(퍼펫)',
#                     value='물리 공격력 : ' + format(int(ACTIVE_BUFF1_AD * 1.25), ',') + '\r\n' +
#                           '마법 공격력 : ' + format(int(ACTIVE_BUFF1_AP * 1.25), ',') + '\r\n' +
#                           '독립 공격력 : ' + format(int(ACTIVE_BUFF1_ID * 1.25), ',') + '\r\n' +
#                           '힘, 지능 : '    + format(int(ACTIVE_BUFF1_STR * 1.25), ','))
#     embed.add_field(itemName='> 금단의 저주(퍼펫 + 편애)',
#                     value='물리 공격력 : ' + format(int(ACTIVE_BUFF1_AD * 1.25 * 1.15), ',') + '\r\n' +
#                           '마법 공격력 : ' + format(int(ACTIVE_BUFF1_AP * 1.25 * 1.15), ',') + '\r\n' +
#                           '독립 공격력 : ' + format(int(ACTIVE_BUFF1_ID * 1.25 * 1.15), ',') + '\r\n' +
#                           '힘, 지능 : '    + format(int(ACTIVE_BUFF1_STR * 1.25 * 1.15), ','))
#     embed.add_field(itemName='> 마리오네트',
#                     value='힘, 지능 : ' + format(ACTIVE_BUFF2_STAT, ','))
#     embed.add_field(itemName='> 종막극',
#                     value='힘, 지능 : ' + format(ACTIVE_BUFF3_STAT, ','))
#     embed.add_field(itemName='> 소악마',
#                     value='힘, 지능 : ' + format(PASSIVE_BUFF_STAT, ','))
#     embed.add_field(itemName='> 버프력',
#                     value=format(TOTAL, ','))
#     embed.set_footer(text='실제 버프 수치와 결과값이 다를 수 있어요!')
#     await ctx.channel.send(embed=embed)