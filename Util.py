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
                if m.content == '':
                    return False
                else:
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
            await ctx.channel.send('해당 캐릭터를 찾을 수 없어요. 다시 한번 확인해주세요!')
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
                if m.content == '':
                    return False
                else:
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
                if m.content == '':
                    return False
                else:
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
