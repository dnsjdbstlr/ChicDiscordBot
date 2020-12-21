import discord
import asyncio

async def getSelectionFromChrIdList(bot, ctx, chrIdList):
    # 여러개가 검색됬을 경우
    if len(chrIdList) >= 2:
        await ctx.channel.purge(limit=1)
        embed = discord.Embed(title='알고싶은 캐릭터의 번호를 입력해주세요!', description='15초만 기다려드릴거에요. 빠르게 골라주세요!')
        for i in range(len(chrIdList)):
            value = 'Lv. ' + chrIdList[i]['level'] + ' ' + chrIdList[i]['characterName'] + '\r\n' + \
                    chrIdList[i]['server'] + ' | ' + chrIdList[i]['jobGrowName']
            embed.add_field(name='> ' + str(i + 1), value=value)
        await ctx.channel.send(embed=embed)

        ### 반응을 대기함 ###
        try:
            def check(m):
                if m.content == '' and ctx.channel.id == m.channel.id:
                    return False
                elif ctx.channel.id == m.channel.id:
                    return True
            msg = await bot.wait_for('message', check=check, timeout=15)

        ### 시간 종료 ###
        except asyncio.TimeoutError:
            await ctx.channel.purge(limit=1)
            await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
            return False

        ### 입력했을 경우 ###
        else:
            await ctx.channel.purge(limit=2)
            try:
                index = int(msg.content) - 1
                server, chrId, name = chrIdList[index]['server'], chrIdList[index]['characterId'], chrIdList[index]['characterName']
            except:
                await ctx.channel.send('> 제대로 입력해주셔야해요! 다시 시도해주세요!')
                return False

    # 한 개가 검색됬을 경우
    else:
        try:
            await ctx.channel.purge(limit=1)
            server, chrId, name = chrIdList[0]['server'], chrIdList[0]['characterId'], chrIdList[0]['characterName']
        except:
            await ctx.channel.send('> 해당 캐릭터를 찾을 수 없어요. 다시 한번 확인해주세요!')
            return False

    return server, chrId, name

async def getSelectionFromItemIdList(bot, ctx, itemIdList):
    if not len(itemIdList):
        await ctx.channel.send('> 해당 장비를 찾을 수 없어요.\r\n> 장비 이름을 확인하고 다시 불러주세요!')
        return False

    if len(itemIdList) >= 2:
        await ctx.channel.purge(limit=1)
        embed = discord.Embed(title='알고싶은 장비 아이템의 번호를 입력해주세요!', description='10초만 기다려드릴거에요. 빠르게 골라주세요!')
        for i in range(len(itemIdList)):
            embed.add_field(name='> ' + str(i + 1), value=itemIdList[i]['itemName'])
        await ctx.channel.send(embed=embed)

        try:
            def check(m):
                if m.content == '' and ctx.channel.id == m.channel.id:
                    return False
                elif ctx.channel.id == m.channel.id:
                    return True
            msg = await bot.wait_for('message', check=check, timeout=10)

        except asyncio.TimeoutError:
            await ctx.channel.purge(limit=1)
            await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
            return
        else:
            await ctx.channel.purge(limit=2)
            try:
                itemId = itemIdList[int(msg.content) - 1]['itemId']
            except:
                await ctx.channel.send('> 제대로 입력해주셔야해요! 다시 시도해주세요!')
                return False
    else:
        await ctx.channel.purge(limit=1)
        itemId = itemIdList[0]['itemId']
    return itemId

async def getSelectionFromSetItemIdList(bot, ctx, setItemIdList):
    if not len(setItemIdList):
        await ctx.channel.send('해당 세트를 찾을 수 없어요...\r\n세트 이름을 확인하고 다시 불러주세요!')
        return

    if len(setItemIdList) >= 2:
        await ctx.channel.purge(limit=1)
        embed = discord.Embed(title='알고싶은 세트옵션의 번호를 입력해주세요!', description='10초만 기다려드릴거에요. 빠르게 골라주세요!')
        for i in range(len(setItemIdList)):
            embed.add_field(name='> ' + str(i + 1), value=setItemIdList[i]['setItemName'])
        await ctx.channel.send(embed=embed)

        try:
            def check(m):
                if m.content == '' and ctx.channel.id == m.channel.id:
                    return False
                elif ctx.channel.id == m.channel.id:
                    return True
            msg = await bot.wait_for('message', check=check, timeout=10)
        except asyncio.TimeoutError:
            await ctx.channel.purge(limit=1)
            await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
            return False
        else:
            await ctx.channel.purge(limit=2)
            try:
                setItemId, setItemName = setItemIdList[int(msg.content) - 1]['setItemId'], setItemIdList[int(msg.content) - 1]['setItemName']
            except:
                await ctx.channel.send('> 제대로 입력해주셔야해요! 다시 시도해주세요!')
                return False
    else:
        await ctx.channel.purge(limit=1)
        setItemId, setItemName = setItemIdList[0]['setItemId'], setItemIdList[0]['setItemName']
    return setItemId, setItemName

def getSirocoItemInfo(chrEquipItemInfo):
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
        '넥스':   0,
        '암살자': 0,
        '록시':   0,
        '수문장': 0,
        '로도스': 0
    }

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
                        reverberation.update({'1옵션' : j['explain']})
                    else:
                        reverberation.update({'2옵션': j['explain']})
                elif i['slotName'] == '하의':
                    if intangible.get('1옵션') is None:
                        intangible.update({'1옵션' : j['explain']})
                        intangibleType = i['upgradeInfo']['itemName']
                    else:
                        intangible.update({'2옵션': j['explain']})
                        intangibleType = i['upgradeInfo']['itemName']

                elif i['slotName'] == '반지':
                    if unconscious.get('1옵션') is None:
                        unconscious.update({'1옵션' : j['explain']})
                        unconsciousType = i['upgradeInfo']['itemName']
                    else:
                        unconscious.update({'2옵션': j['explain']})
                        unconsciousType = i['upgradeInfo']['itemName']
                elif i['slotName'] == '보조장비':
                    if illusion.get('1옵션') is None:
                        illusion.update({'1옵션' : j['explain']})
                        illusionType = i['upgradeInfo']['itemName']
                    else:
                        illusion.update({'2옵션': j['explain']})
                        illusionType = i['upgradeInfo']['itemName']
        except: pass

    sirocoInfo['세트'] = setCount
    if len(reverberation)   != 0: sirocoInfo['잔향'] = reverberation
    if len(intangible)      != 0: sirocoInfo[intangibleType] = intangible
    if len(unconscious)     != 0: sirocoInfo[unconsciousType] = unconscious
    if len(illusion)        != 0: sirocoInfo[illusionType] = illusion

    if len(reverberation) == 0 and len(intangible) == 0 and len(unconscious) == 0 and len(illusion) == 0:
        return None
    else:
        return sirocoInfo
