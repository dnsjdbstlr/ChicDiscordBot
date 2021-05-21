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
            if j['name'] in MAX_OPTION[i['itemId']].keys():
                diff = j['value'] - MAX_OPTION[i['itemId']][j['name']]
                value += j['name'] + ' : ' + str(j['value']) + '(' + str(diff) + ')\r\n'
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
    def MAKE_EMBED(eChrName, eChrEquipItemInfo, eChrEquipSetInfo, eAvatar=None, eServer=None, eChrId=None):
        eEmbed = discord.Embed(title=f"{eChrName}님의 캐릭터 정보를 알려드릴게요.")

        if eAvatar is not None:
            for a in eAvatar['avatar']:
                if a['slotName'] == '오라 아바타': continue
                eValue = f"{a['itemName']}\n"
                if a['clone']['itemName'] is not None:
                    eValue += f"{a['clone']['itemName']}"
                eEmbed.add_field(name=f"> {a['slotName']}", value=eValue)
            eEmbed.set_image(url=DNFAPI.getChrImageUrl(eServer, eChrId))
            return eEmbed
        else:
            ### 장착중인 세트 ###
            eValue = ''
            for eSetInfo in eChrEquipSetInfo['setItemInfo']:
                eValue += f"{eSetInfo['setItemName']}({eSetInfo['activeSetNo']})\n"
            if eValue != '': eEmbed.add_field(name='> 장착중인 세트', value=eValue, inline=False)

            ### 장비 옵션 ###
            for eItemInfo in eChrEquipItemInfo['equipment']:
                if eItemInfo['slotName'] in ['칭호', '보조무기']: continue

                eValue = ''

                ### 강화, 재련 수치 ###
                if eItemInfo['reinforce'] != 0:
                    eValue += f"+{eItemInfo['reinforce']}"
                if eItemInfo['refine'] != 0:
                    eValue += f"({eItemInfo['refine']})"
                eValue += f" {eItemInfo['itemName']}\n"

                ### 마법부여 ###
                try:
                    for eEnchant in eItemInfo['enchant']['status']:
                        eValue += f"{eEnchant['name']} +{eEnchant['value']}\n"
                except: pass

                eEmbed.add_field(name='> ' + eItemInfo['slotName'], value=eValue)

            return eEmbed

    if not input:
        await ctx.message.delete()
        await ctx.channel.send('> !캐릭터 <닉네임> 또는 !캐릭터 <서버> <닉네임> 의 형태로 적어야해요!')
        return

    if len(input) == 2:
        server  = input[0]
        chrName = input[1]
    else:
        server  = '전체'
        chrName = input[0]

    try:
        chrIdList = DNFAPI.getChrIdList(server, chrName)
        server, chrId, chrName = await Util.getSelectionFromChrIdList(bot, ctx, chrIdList)
    except: return False

    message = await ctx.channel.send(f"> {chrName} 캐릭터의 정보를 불러오고 있어요...")

    chrEquipItemInfo = DNFAPI.getChrEquipItems(server, chrId)
    chrEquipItemIds  = []
    for i in chrEquipItemInfo['equipment']:
        if i['slotName'] in ['칭호', '보조무기']: continue
        chrEquipItemIds.append(i['itemId'])
    chrEquipSetInfo = DNFAPI.getEquipActiveSet(','.join(chrEquipItemIds))

    isAvatar = False
    avatar = None
    embed = MAKE_EMBED(chrName, chrEquipItemInfo, chrEquipSetInfo)
    await message.edit(embed=embed, content=None)
    await message.add_reaction('🔄')
    
    while True:
        try:
            def check(_reaction, _user):
                return str(_reaction) == '🔄' and _user == ctx.author and _reaction.message.id == message.id
            reaction, user = await bot.wait_for('reaction_add', check=check)

            isAvatar = not isAvatar
            if isAvatar:
                if avatar is None: avatar = DNFAPI.getChrEquipAvatar(server, chrId)
                embed = MAKE_EMBED(chrName, chrEquipItemInfo, chrEquipSetInfo, avatar, server, chrId)
            else:
                embed = MAKE_EMBED(chrName, chrEquipItemInfo, chrEquipSetInfo)
            await message.edit(embed=embed)
            await message.clear_reactions()
            await message.add_reaction('🔄')

        except Exception as e:
            await message.edit(content=f"> 오류가 발생했습니다.\n> {e}")
            return

async def 시세(bot, ctx, *input):
    def MAKE_EMBED(eItemName):
        eAuction = DNFAPI.getItemAuction(eItemName)

        eEmbed = discord.Embed(title=f"'{eItemName}' 시세를 알려드릴게요")
        if '카드' in eItemName:
            eUpgrades = list(set([int(i['upgrade']) for i in eAuction]))
            eUpgrades.sort()

            for eUpgrade in eUpgrades:
                # 가격 계산
                eSum, eCount = 0, 0
                for i in eAuction:
                    if eUpgrade == int(i['upgrade']):
                        eSum += i['price']
                        eCount += i['count']
                ePrice = eSum // eCount

                # 최신화
                Tool.updateAuctionPrice(f"{eItemName} +{eUpgrade}", ePrice)

                # 필드 추가
                ePrev = Tool.getPrevPrice(f"{eItemName} +{eUpgrade}")
                eEmbed.add_field(name=f"> {eUpgrade} 평균 가격", value=f"{format(ePrice, ',')}골드")
                eEmbed.add_field(name='> 최근 판매량', value=f"{format(eCount, ',')}개")
                if ePrev is None:
                    eEmbed.add_field(name='> 가격 변동률', value='데이터 없음')
                else:
                    eEmbed.add_field(name='> 가격 변동률',
                                     value=f"{Util.getVolatility(ePrev['price'], ePrice)} ({ePrev['date'].strftime('%Y-%m-%d')})")
        else:
            # 가격 계산
            eSum, eCount = 0, 0
            for i in eAuction:
                eSum += i['price']
                eCount += i['count']
            ePrice = eSum // eCount

            # 최신화
            Tool.updateAuctionPrice(eItemName, ePrice)

            # 필드 추가
            ePrev = Tool.getPrevPrice(eItemName)
            eEmbed.add_field(name='> 평균 가격', value=format(ePrice, ',') + '골드')
            eEmbed.add_field(name='> 최근 판매량', value=format(eCount, ',') + '개')
            if ePrev is None:
                eEmbed.add_field(name='> 가격 변동률', value='데이터 없음')
            else:
                eEmbed.add_field(name='> 가격 변동률',
                                 value=f"{Util.getVolatility(ePrev['price'], ePrice)} ({ePrev['date'].strftime('%Y-%m-%d')})")

        eEmbed.set_footer(text=eAuction[-1]['soldDate'] + ' 부터 ' + eAuction[0]['soldDate'] + ' 까지 집계된 자료예요.')
        eEmbed.set_thumbnail(url=DNFAPI.getItemImageUrl(eAuction[0]['itemId']))
        return eEmbed

    await ctx.message.delete()
    message = await ctx.channel.send('> 아이템 시세 정보를 불러오고 있어요...')

    item = DNFAPI.getMostSimilarItem(' '.join(input))
    if item is None:
        await message.delete()
        await ctx.channel.send('> 해당 아이템의 판매 정보를 얻어오지 못했어요.')
        return

    embed = MAKE_EMBED(item['itemName'])
    await message.edit(embed=embed, content=None)
    await message.add_reaction('🔄')

    while True:
        try:
            def check(_reaction, _user):
                return str(_reaction) == '🔄' and _user == ctx.author and _reaction.message.id == message.id
            reaction, user = await bot.wait_for('reaction_add', check=check)

            # 로딩
            embed.set_footer(text='시세 정보를 불러오고 있어요...')
            await message.edit(embed=embed, content=None)
            await message.clear_reactions()

            # 최신화
            embed = MAKE_EMBED(item['itemName'])
            await message.edit(embed=embed)
            await message.add_reaction('🔄')

        except Exception as e:
            await message.edit(content=f"> 오류가 발생했어요.\n> {e}", embed=None)
            return

async def 장비(bot, ctx, *itemName):
    def MAKE_EMBED(eItemInfo, eIsBuff):
        from Src import Measure

        eDesc = f"{eItemInfo['itemAvailableLevel']} Lv {eItemInfo['itemRarity']} {eItemInfo['itemTypeDetail']}"
        eEmbed = discord.Embed(title=eItemInfo['itemName'], description=eDesc)
        if eIsBuff:
            # 스탯
            statInfo = DNFAPI.getItemStatInfo(eItemInfo['itemStatus'])
            eEmbed.add_field(name='> 스탯', value=statInfo, inline=False)

            # 시로코 옵션
            try:
                sirocoInfo = ''
                for i in eItemInfo['sirocoInfo']['options']:
                    buffExplainDetail = i['buffExplainDetail'].replace('\n\n', '\n')
                    sirocoInfo += f"{buffExplainDetail}\n"
                eEmbed.add_field(name='> 시로코 옵션', value=sirocoInfo, inline=False)
            except: pass

            # 버프 스킬 레벨 옵션
            try:
                buffLvInfo = Measure.getSkillLevelingInfo(eItemInfo['itemBuff']['reinforceSkill'])
                buffLvInfoValue = ''
                for key in buffLvInfo.keys():
                    if key != '모든 직업': buffLvInfoValue += f"{key}\n"
                    for lv in buffLvInfo[key]:
                        if key != '모든 직업':
                            buffLvInfoValue += f"{lv}\n"
                        else:
                            buffLvInfoValue += f"{key} {lv}\n"

                # 버프 옵션
                buffInfo = eItemInfo['itemBuff']['explain']
                eEmbed.add_field(name='> 버퍼 전용 옵션', value=buffLvInfoValue + buffInfo, inline=False)
            except: pass

            # 신화 옵션
            try:
                mythicInfo = DNFAPI.getItemMythicInfo(eItemInfo['mythologyInfo']['options'], buff=True)
                eEmbed.add_field(name='> 신화 전용 옵션', value=mythicInfo)
            except: pass

            # 플레이버 텍스트
            eEmbed.set_footer(text=eItemInfo['itemFlavorText'])

            # 아이콘
            icon = DNFAPI.getItemImageUrl(eItemInfo['itemId'])
            eEmbed.set_thumbnail(url=icon)

            return eEmbed
        else:
            # 스탯
            eStatInfo = DNFAPI.getItemStatInfo(eItemInfo['itemStatus'])
            eEmbed.add_field(name='> 스탯', value=eStatInfo, inline=False)

            # 시로코 옵션
            try:
                sirocoInfo = ''
                for i in eItemInfo['sirocoInfo']['options']:
                    sirocoInfo += f"{i['explainDetail']}\n"
                eEmbed.add_field(name='> 시로코 옵션', value=sirocoInfo, inline=False)
            except: pass

            # 스킬 레벨
            try:
                eSkillLvInfo = DNFAPI.getItemSkillLvInfo(eItemInfo['itemReinforceSkill'][0]['jobName'],
                                                         eItemInfo['itemReinforceSkill'][0]['levelRange'])
                eEmbed.add_field(name='> 스킬', value=eSkillLvInfo)
            except: pass

            # 기본 옵션
            if eItemInfo['itemExplainDetail'] != '':
                eEmbed.add_field(name='> 옵션', value=eItemInfo['itemExplainDetail'], inline=False)

            # 변환 옵션
            try:
                eTransformInfo = eItemInfo['transformInfo']['explain']
                eEmbed.add_field(name='> 변환 옵션', value=eTransformInfo, inline=False)
            except: pass

            # 신화옵션
            try:
                eMythicInfo = DNFAPI.getItemMythicInfo(eItemInfo['mythologyInfo']['options'])
                eEmbed.add_field(name='> 신화 전용 옵션', value=eMythicInfo, inline=False)
            except: pass

            # 플레이버 텍스트
            try:
                eFlavorText = eItemInfo['itemFlavorText']
                eEmbed.set_footer(text=eFlavorText)
            except: pass

            # 아이콘
            eIcon = DNFAPI.getItemImageUrl(eItemInfo['itemId'])
            eEmbed.set_thumbnail(url=eIcon)

            return eEmbed

    itemName = ' '.join(itemName)
    if len(itemName) < 1:
        await ctx.message.delete()
        await ctx.channel.send('> !장비 <장비템이름> 의 형태로 적어야해요!')
        return

    try:
        itemIdList = DNFAPI.getItem(itemName)
        itemId = await Util.getSelectionFromItemIdList(bot, ctx, itemIdList)
        if itemId is False: return
    except: return

    itemInfo = DNFAPI.getItemDetail(itemId)
    message = await ctx.channel.send(f"> {itemInfo['itemName']}의 정보를 불러오고 있어요...")

    isBuff = False
    embed = MAKE_EMBED(itemInfo, isBuff)
    await message.edit(embed=embed, content=None)
    await message.add_reaction('🔄')

    while True:
        try:
            def check(_reaction, _user):
                return str(_reaction) == '🔄' and _user == ctx.author and _reaction.message.id == message.id
            reaction, user = await bot.wait_for('reaction_add', check=check)

            isBuff = not isBuff
            embed = MAKE_EMBED(itemInfo, isBuff)
            await message.edit(embed=embed, content=None)
            await message.clear_reactions()
            await message.add_reaction('🔄')

        except Exception as e:
            await message.edit(content=f"> 오류가 발생했어요.\n> {e}", embed=None)
            return

async def 세트(bot, ctx, *setName):
    def MAKE_EMBED(eSetItemInfo, eIsBuff):
        from Src import Measure

        if eIsBuff:
            eEmbed = discord.Embed(title=f"{eSetItemInfo['setItemName']}의 정보를 알려드릴게요.")
            for setItem in eSetItemInfo['setItems']:
                eName = f"> {setItem['itemRarity']} {setItem['slotName']}"
                eValue = setItem['itemName']
                eEmbed.add_field(name=eName, value=eValue)

            for option in eSetItemInfo['setItemOption']:
                skill = Measure.getSkillLevelingInfo(option['itemBuff']['reinforceSkill'])

                value = ''
                for key in skill.keys():
                    if key != '모든 직업': value += f"{key}\n"
                    for lv in skill[key]:
                        if key != '모든 직업':
                            value += f"{lv}\n"
                        else:
                            value += f"{key} {lv}\n"
                value += option['itemBuff']['explain']
                eEmbed.add_field(name='> ' + str(option['optionNo']) + '세트 옵션', value=value, inline=False)
            eEmbed.set_thumbnail(url=DNFAPI.getItemImageUrl(eSetItemInfo['setItems'][0]['itemId']))
            return eEmbed

        else:
            eEmbed = discord.Embed(title=setItemInfo['setItemName'] + '의 정보를 알려드릴게요.')
            for setItem in setItemInfo['setItems']:
                eEmbed.add_field(name='> ' + setItem['itemRarity'] + ' ' + setItem['slotName'],
                                 value=setItem['itemName'])
            for option in setItemInfo['setItemOption']:
                value = ''
                try:
                    for status in option['status']:
                        value += status['itemName'] + ' ' + status['value'] + '\r\n'
                except:
                    pass
                eEmbed.add_field(name='> ' + str(option['optionNo']) + '세트 옵션', value=value + option['explain'], inline=False)
            eEmbed.set_thumbnail(url=DNFAPI.getItemImageUrl(setItemInfo['setItems'][0]['itemId']))
            return eEmbed

    name = ' '.join(setName)
    if len(name) < 1:
        await ctx.message.delete()
        await ctx.channel.send('> !세트 <세트옵션이름> 의 형태로 적어야해요!')
        return

    try:
        setItemIdList = DNFAPI.getSetItemIdList(name)
        setItemId, setItemName = await Util.getSelectionFromSetItemIdList(bot, ctx, setItemIdList)
    except: return

    message = await ctx.channel.send(f"> {setItemName}의 정보를 불러오고 있어요...")

    isBuff = False
    setItemInfo = DNFAPI.getSetItemInfo(setItemId)
    embed = MAKE_EMBED(setItemInfo, isBuff)
    await message.edit(embed=embed, content=None)
    await message.add_reaction('🔄')

    while True:
        try:
            def check(_reaction, _user):
                return str(_reaction) == '🔄' and _user == ctx.author and _reaction.message.id == message.id
            reaction, user = await bot.wait_for('reaction_add', check=check)

            isBuff = not isBuff
            embed = MAKE_EMBED(setItemInfo, isBuff)
            await message.edit(embed=embed)
            await message.clear_reactions()
            await message.add_reaction('🔄')

        except Exception as e:
            await message.edit(content=f"> 오류가 발생했어요\n> {e}", embed=None)
            return

async def 에픽(bot, ctx, *input):
    def MAKE_EMBED(eNickname, eTimeline, eChannel, ePage):
        if eChannel == '없음':
            eEmbed = discord.Embed(title=f'{eNickname} 님은 이번 달에 {len(eTimeline)}개의 에픽을 획득했어요.')
        else:
            eEmbed = discord.Embed(title=f'{eNickname} 님은 이번 달에 {len(eTimeline)}개의 에픽을 획득했어요.',
                                   description=f'`{eChannel}`에서 에픽을 가장 많이 획득했어요!')
        for t in eTimeline[ePage * 15:ePage * 15 + 15]:
            if t['code'] == 505:
                eName = f"> {t['date'][:10]}\n" \
                        f"ch{t['data']['channelNo']}.{t['data']['channelName']}"
                eValue = t['data']['itemName']
            elif t['code'] == 513:
                eName = f"> {t['date'][:10]}\n" \
                        f"{t['data']['dungeonName']}"
                eValue = t['data']['itemName']
            else: continue
            eEmbed.add_field(name=eName, value=eValue)
        eEmbed.set_footer(text=f"{ePage + 1}페이지 / {(len(eTimeline) - 1) // 15 + 1}페이지")
        return eEmbed

    def GET_LUCKY_CHANNEL(eTimeline):
        eChannels = {}
        for i in eTimeline:
            if i['code'] == 505:
                eChannels.setdefault(f"ch{i['data']['channelNo']}.{i['data']['channelName']}", 0)
                eChannels[f"ch{i['data']['channelNo']}.{i['data']['channelName']}"] += 1

        if eChannels == {}:
            return '없음'
        else:
            return sorted(eChannels.items(), key=lambda x: x[1], reverse=True)[0][0]

    if not input:
        await ctx.message.delete()
        await ctx.channel.send('> `!에픽 <닉네임>` 또는 `!에픽 <서버> <닉네임>` 의 형태로 적어야해요!')
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

    message = await ctx.channel.send(f"> {name}님의 타임라인을 불러오고 있어요...")

    # 획득한 에픽이 없는 경우
    timeline = DNFAPI.getChrTimeLine(server, chrId, 505, 513)
    if len(timeline) == 0:
        await message.edit(f'> {name}님은 이번 달 획득한 에픽이 없어요.. ㅠㅠ')
        return

    # 에픽을 가장 많이 획득한 채널
    channel = GET_LUCKY_CHANNEL(timeline)

    # 에픽랭킹 등록
    Tool.updateEpicRank(server, name, len(timeline), channel)

    page = 0
    embed = MAKE_EMBED(name, timeline, channel, page)
    await message.edit(embed=embed, content=None)

    if len(timeline) > 15:
        await message.add_reaction('▶️')
    while len(timeline) > 15:
        try:
            def check(_reaction, _user):
                return str(_reaction) in ['◀️', '▶️'] and _user == ctx.author and _reaction.message.id == message.id
            reaction, user = await bot.wait_for('reaction_add', check=check)

            if str(reaction) == '◀️' and page > 0:
                page -= 1
            if str(reaction) == '▶️' and page < (len(timeline) - 1) // 15:
                page += 1

            embed = MAKE_EMBED(name, timeline, channel, page)
            await message.edit(embed=embed)
            await message.clear_reactions()

            if page > 0:
                await message.add_reaction('◀️')
            if page < (len(timeline) - 1) // 15:
                await message.add_reaction('▶️')
        except Exception as e:
            await message.edit(content=f"> 오류가 발생했습니다.\n> {e}", embed=None)
            return

async def 에픽랭킹(bot, ctx):
    def MAKE_EMBED(eRank, ePage):
        eToday = datetime.today()
        eRank = eRank[ePage * 15:ePage * 15 + 15]
        eEmbed = discord.Embed(title=f"{eToday.year}년 {eToday.month}월 기린 랭킹을 알려드릴게요!")
        for idx, r in enumerate(eRank):
            eEmbed.add_field(name=f"> {ePage * 15 + idx + 1}등\n"
                                  f"> {r['server']} {r['name']}",
                             value=f"개수 : {r['count']}개\n"
                                   f"채널 : {r['channel']}")
        eEmbed.set_footer(text=f"{ePage + 1}페이지 / {(len(eRank) - 1) // 15 + 1}페이지")
        return eEmbed

    await ctx.message.delete()
    message = await ctx.channel.send('> 에픽 랭킹을 불러오는 중이예요...')

    rank = Tool.getEpicRanks()
    rank = list(sorted(rank, key=lambda x: x['count'], reverse=True))
    if not rank:
        today = datetime.today()
        embed = discord.Embed(title=f'{today.year}년 {today.month}월 에픽 랭킹을 알려드릴게요!',
                              description='> 에픽 랭킹 데이터가 없어요.\n'
                                          '> `!에픽` 명령어를 사용해서 랭킹에 등록해보세요!')
        await message.edit(embed=embed, content=None)
        return

    page = 0
    embed = MAKE_EMBED(rank, page)
    await message.edit(embed=embed, content=None)
    if len(rank) > 15: await message.add_reaction('▶️')

    while len(rank) > 15:
        try:
            def check(_reaction, _user):
                return str(_reaction) in ['◀️', '▶️'] and _user == ctx.author and _reaction.message.id == message.id
            reaction, user = await bot.wait_for('reaction_add', check=check)

            if str(reaction) == '◀️' and page > 0:
                page -= 1
            if str(reaction) == '▶️' and page < (len(rank) - 1) // 15:
                page += 1

            embed = MAKE_EMBED(rank, page)
            await message.edit(embed=embed)
            await message.clear_reactions()

            if page > 0:
                await message.add_reaction('◀️')
            if page < (len(rank) - 1) // 15:
                await message.add_reaction('▶️')
        except Exception as e:
            await message.edit(content=f"> 오류가 발생했습니다.\n> {e}", embed=None)
            return

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