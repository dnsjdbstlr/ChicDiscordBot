import json
import discord
from Src import DNFAPI, Util
from Database import Tool

async def 강화설정(bot, ctx, *input):
    did, name = ctx.message.author.id, ctx.message.author.display_name

    # 입력이 잘못되었을 경우
    itemName = Util.mergeString(*input)
    if len(itemName) < 1:
        await ctx.message.delete()
        embed = discord.Embed(title=f"{name}님의 강화 설정",
                              description=f"`!강화설정 '무기아이템이름'` 의 형태로 적어야해요.")
        await ctx.channel.send(embed=embed)
        return

    try:
        itemList = DNFAPI.getItem(itemName, _type='무기')
        item = await Util.getSelectionFromItemIdList(bot, ctx, itemList,
                                                     title=f"{name}님의 강화 설정",
                                                     description='강화에 사용할 무기를 선택해주세요. 15초 안에 선택해야해요.')
        if item is False: return
    except: return
    info = DNFAPI.getItemDetail(item)

    # 저장
    reinforce = Tool.getReinforce(did)
    if reinforce is None:
        Tool.iniReinforce(did, info['itemId'], info['itemName'])
    else:
        Tool.resetReinforce(did, info['itemId'], info['itemName'])

    embed = discord.Embed(title=f"{name}님의 강화 설정", description=f"강화 설정에 성공했습니다. 아래 내용을 확인해주세요.")
    embed.add_field(name='> 레벨제한', value=f"{info['itemAvailableLevel']}레벨")
    embed.add_field(name='> 타입',     value=f"{info['itemRarity']} {info['itemTypeDetail']}")
    embed.add_field(name='> 이름',     value=info['itemName'])
    embed.set_thumbnail(url=DNFAPI.getItemImageUrl(info['itemId']))
    await ctx.channel.send(embed=embed)

async def 강화정보(ctx):
    did, name = ctx.message.author.id, ctx.message.author.display_name
    
    # 강화설정이 안되어있는 경우
    reinforce = Tool.getReinforce(did)
    if reinforce is None:
        await ctx.message.delete()
        embed = discord.Embed(title=f"{name}님의 강화 정보",
                              description=f"`!강화설정 '무기아이템이름'` 명령어를 사용하고 다시 시도해주세요.\r\n"
                                          f"강화하는 데 설정된 무기가 있어야 `!강화` 명령어를 사용할 수 있어요.")
        await ctx.channel.send(embed=embed)
        return

    _max = json.loads(reinforce['max'])
    _try = json.loads(reinforce['try'])

    await ctx.message.delete()
    embed = discord.Embed(title=f"{name}님의 강화 정보")
    embed.add_field(name=f"> 현재 장비", value=f"+{reinforce['value']} {reinforce['itemName']}")
    embed.add_field(name=f"> 최고 강화 수치", value=f"+{_max['value']} {_max['itemName']}")
    embed.add_field(name=f"> 강화 시도", value=f"성공 : {format(_try['success'], ',')}회\r\n"
                                               f"실패 : {format(_try['fail'], ',')}회\r\n"
                                               f"파괴 : {format(_try['destroy'], ',')}회")
    embed.set_thumbnail(url=DNFAPI.getItemImageUrl(reinforce['id']))
    await ctx.channel.send(embed=embed)

async def 강화(bot, ctx):
    did, name = ctx.message.author.id, ctx.message.author.display_name

    # 강화설정이 안되어있는 경우
    reinforce = Tool.getReinforce(did)
    if reinforce is None:
        await ctx.message.delete()
        embed = discord.Embed(title=f"{name}님의 강화",
                              description=f"`!강화설정 '무기아이템이름'` 명령어를 사용하고 다시 시도해주세요.\r\n"
                                          f"강화하는 데 설정된 무기가 있어야 `!강화` 명령어를 사용할 수 있어요.")
        await ctx.channel.send(embed=embed)
        return

    # 계정 생성이 안되어있는 경우
    account = Tool.getAccount(did)
    if account is None:
        Tool.iniAccount(did)

    await ctx.message.delete()
    embed = getReinforceEmbed(ctx, reinforce)
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('⭕')
    await msg.add_reaction('❌')

    while True:
        def check(_reaction, _user):
            return str(_reaction) in ['⭕', '❌'] and _user == ctx.author and _reaction.message.id == msg.id
        reaction, user = await bot.wait_for('reaction_add', check=check)
        
        # 강화 시도
        if str(reaction) == '⭕':
            prob, cost = getReinforceInfo(reinforce['value'] + 1)
            gold = Tool.getGold(did)

            if gold < cost:
                embed.set_footer(text='강화에 필요한 골드가 부족합니다.')
            else:
                result = tryReinforce(did, reinforce)
                reinforce = Tool.getReinforce(did)
                embed = getReinforceEmbed(ctx, reinforce)
                if result: embed.set_footer(text='강화에 성공했습니다.')
                else:      embed.set_footer(text='강화에 실패했습니다.')
            await msg.edit(embed=embed)
            await msg.clear_reactions()
            await msg.add_reaction('⭕')
            await msg.add_reaction('❌')
            
        # 강화 취소
        elif str(reaction) == '❌':
            await msg.clear_reactions()
            embed.set_footer(text='강화가 취소되었습니다.')
            await msg.edit(embed=embed)
            return

async def 공개강화(bot, ctx):
    did, name = ctx.message.author.id, ctx.message.author.display_name
    donationLog, donation = {}, 0 # 기부금

    # 강화설정이 안되어있는 경우
    reinforce = Tool.getReinforce(did)
    if reinforce is None:
        await ctx.message.delete()
        embed = discord.Embed(title=f"{name}님의 공개 강화",
                              description=f"`!강화설정 <무기아이템이름>` 명령어를 사용하고 다시 시도해주세요.\r\n"
                                          f"강화하는 데 설정된 무기가 있어야 `!공개강화` 명령어를 사용할 수 있어요.")
        await ctx.channel.send(embed=embed)
        return

    # 계정 생성이 안되어있는 경우
    account = Tool.getAccount(did)
    if account is None:
        Tool.iniAccount(did)

    await ctx.message.delete()
    embed = getPublicReinforceEmbed(ctx, donationLog, donation, reinforce)
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('⭕')
    await msg.add_reaction('❌')
    await msg.add_reaction('❤️')

    while True:
        def check(_reaction, _user):
            return str(_reaction) in ['⭕', '❌', '❤️'] and _reaction.message.id == msg.id and not _user.bot
        reaction, user = await bot.wait_for('reaction_add', check=check)
        if str(reaction) == '⭕' and user.id == did:
            await msg.clear_reactions()
            prob, cost = getReinforceInfo(reinforce['value'] + 1)

            if Tool.getGold(did) + donation < cost:
                embed.set_footer(text='강화에 필요한 골드가 부족합니다.')
            else:
                result = tryReinforce(did, reinforce)
                reinforce = Tool.getReinforce(did)
                embed = getPublicReinforceEmbed(ctx, donationLog, donation, reinforce)
                if result: embed.set_footer(text='강화에 성공했습니다.')
                else:      embed.set_footer(text='강화에 실패했습니다.')

            await msg.edit(embed=embed)
            await msg.add_reaction('⭕')
            await msg.add_reaction('❌')
            await msg.add_reaction('❤️')

        elif str(reaction) == '❌' and user.id == did:
            await msg.clear_reactions()
            embed.set_footer(text='공개 강화가 취소되었습니다.')
            await msg.edit(embed=embed)
            return

        elif str(reaction) == '❤️':
            await msg.clear_reactions()
            if user.id == did:
                embed.set_footer(text='본인의 공개 강화에는 기부할 수 없습니다.')
                await msg.edit(embed=embed)
            else:
                if Tool.getAccount(user.id) is None:
                    Tool.iniAccount(user.id)

                embed.set_footer(text=f"{user.display_name}님이 기부를 진행 중입니다...")
                await msg.edit(embed=embed)

                gold = await getPublicReinforceDonation(bot, ctx, user)
                if gold > 0:
                    donationLog.setdefault(user.display_name, 0)
                    donationLog[user.display_name] += gold
                    donation += gold

                embed = getPublicReinforceEmbed(ctx, donationLog, donation, reinforce)
                embed.set_footer(text=f"{user.display_name}님이 {format(gold, ',')}골드를 기부했어요!")
                await msg.edit(embed=embed)
            await msg.add_reaction('⭕')
            await msg.add_reaction('❌')
            await msg.add_reaction('❤️')

async def 강화랭킹(bot, ctx):
    await ctx.message.delete()
    waiting = await ctx.channel.send('> 강화 랭킹을 불러오는 중이예요...')

    page = 0
    rank = Tool.getReinforce()

    embed = getReinforceRankEmbed(rank=rank, page=page, user=ctx.message.author)
    embed.set_footer(text=f'{(len(rank) - 1) // 15 + 1}쪽 중 1쪽')
    await waiting.delete()
    msg = await ctx.channel.send(embed=embed)

    if len(rank) > 15:
        await msg.add_reaction('▶️')
    while len(rank) > 15:
        def check(_reaction, _user):
            return str(_reaction) in ['◀️', '▶️'] and _user == ctx.author and _reaction.message.id == msg.id
        reaction, user = await bot.wait_for('reaction_add', check=check)

        if str(reaction) == '◀️' and page > 0:
            page -= 1
        if str(reaction) == '▶️' and page < (len(rank) - 1) // 15:
            page += 1

        embed = getReinforceRankEmbed(rank=rank, page=page, user=ctx.message.author)
        embed.set_footer(text=f'{(len(rank) - 1) // 15 + 1}쪽 중 {page + 1}쪽')
        await msg.edit(embed=embed)
        await msg.clear_reactions()

        if page > 0:
            await msg.add_reaction('◀️')
        if page < (len(rank) - 1) // 15:
            await msg.add_reaction('▶️')

async def getPublicReinforceDonation(bot, ctx, user):
    gold = Tool.getGold(user.id)

    embed = discord.Embed(title=f"{user.display_name}님의 공개 강화 기부",
                          description=f"{ctx.message.author.display_name}님에게 기부할 골드를 입력해주세요.\r\n"
                                      f"한번 기부한 골드는 회수할 수 없습니다. 신중히 입력해주세요.")
    embed.add_field(name='> 보유 골드', value=f"{format(gold, ',')}골드")
    embed.set_footer(text='20초 안에 입력해야해요.')
    message = await ctx.channel.send(embed=embed)

    def check(_message): return ctx.channel.id == _message.channel.id and user == _message.author
    answer = await bot.wait_for('message', check=check, timeout=20)
    try:
        if gold < int(answer.content):
            await answer.delete()
            embed = discord.Embed(title=f"{user.display_name}님의 공개 강화 기부",
                                  description=f"보유 골드보다 많이 기부할 수 없어요. 다시 시도해주세요.")
            await message.edit(embed=embed)
            return -1
        elif int(answer.content) <= 0:
            await answer.delete()
            embed = discord.Embed(title=f"{user.display_name}님의 공개 강화 기부",
                                  description=f"기부는 1골드 이상만 하실 수 있어요. 다시 시도해주세요.")
            await message.edit(embed=embed)
            return -1
        else:
            await answer.delete()
            await message.delete()
            Tool.gainGold(user.id, -int(answer.content))
            return int(answer.content)
    except:
        embed = discord.Embed(title=f"{user.display_name}님의 공개 강화 기부",
                              description=f"입력이 잘못되었어요. 다시 시도해주세요.")
        await message.edit(embed=embed)
        return -1

def getReinforceInfo(value):
    prob = {
        1 : 100,
        2 : 100,
        3 : 100,
        4 : 100,
        5 : 80,
        6 : 70,
        7 : 60,
        8 : 50,
        9 : 40,
        10 : 30,
        11 : 25,
        12 : 18,
        13 : 17,
        14 : 16,
        15 : 14,
    }

    cost = {
        1 : 354600,
        2 : 354600,
        3 : 354600,
        4 : 354600,
        5 : 709200,
        6 : 780120,
        7 : 851040,
        8 : 921960,
        9 : 992880,
        10 : 1063800,
        11 : 1063800,
        12 : 1773000,
        13 : 2836800,
        14 : 4255200,
        15 : 6028200
    }

    return prob[value], cost[value]

def tryReinforce(did, reinforce):
    prob, cost = getReinforceInfo(reinforce['value'] + 1)

    import random
    seed = random.randint(1, 100)
    if seed <= prob:
        Tool.setReinforceValue(did, reinforce['value'] + 1)
        Tool.incReinforceTry(did, 'success')

        _max = Tool.getReinforceMax(did)
        if _max['value'] < reinforce['value'] + 1:
            _max['itemName'] = reinforce['itemName']
            _max['value'] = reinforce['value'] + 1
            Tool.setReinforceMax(did, _max)
        success = True
    else:
        if 10 <= reinforce['value'] <= 11:
            Tool.setReinforceValue(did, reinforce['value'] - 3)
        elif reinforce['value'] >= 12:
            Tool.setReinforceValue(did, 0)

        if reinforce['value'] < 12:
            Tool.incReinforceTry(did, 'fail')
        else:
            Tool.incReinforceTry(did, 'destroy')
        success = False
    Tool.gainGold(did, -cost)
    return success

def getReinforceEmbed(ctx, reinforce):
    did, name = ctx.message.author.id, ctx.message.author.display_name
    prob, cost = getReinforceInfo(reinforce['value'] + 1)

    embed = discord.Embed(title=f"{name}님의 강화", description=f"강화를 시도하려면 ⭕, 취소하려면 ❌ 이모지를 추가해주세요.")
    embed.add_field(name=f"> 장비", value=f"+{reinforce['value']} {reinforce['itemName']}", inline=False)
    embed.add_field(name=f"> 성공 확률", value=f"{prob}%")
    embed.add_field(name=f"> 소모 골드", value=f"{format(cost, ',')}골드")
    embed.add_field(name=f"> 보유 골드", value=f"{format(Tool.getGold(did), ',')}골드")
    embed.set_thumbnail(url=DNFAPI.getItemImageUrl(reinforce['id']))
    return embed

def getPublicReinforceEmbed(ctx, donationLog, donation, reinforce):
    did, name = ctx.message.author.id, ctx.message.author.display_name
    prob, cost = getReinforceInfo(reinforce['value'] + 1)

    embed = discord.Embed(title=f"{name}님의 공개 강화",
                          description=f"강화를 시도하려면 ⭕, 취소하려면 ❌, 기부하려면 ❤️이모지를 추가해주세요."
                                      f"기부한 골드는 회수할 수 없고 강화를 취소하면 기부 골드는 모두 소멸됩니다.")
    embed.add_field(name=f"> 장비", value=f"+{reinforce['value']} {reinforce['itemName']}")
    embed.add_field(name=f"> 성공 확률", value=f"{prob}%")
    embed.add_field(name=f"> 소모 골드", value=f"{format(cost, ',')}골드")
    embed.add_field(name=f"> 보유 골드", value=f"{format(Tool.getGold(did), ',')}골드")
    embed.add_field(name=f"> 기부 골드", value=f"{format(donation, ',')}골드")
    if donationLog == {}:
        embed.add_field(name='> 기부 내역', value='없음')
    else:
        value = ''
        for index, key in enumerate(donationLog):
            value += f"{key}님 : {format(donationLog[key], ',')}골드\r\n"
        embed.add_field(name='> 기부 내역', value=value)
    embed.set_thumbnail(url=DNFAPI.getItemImageUrl(reinforce['id']))
    return embed

def getReinforceRankEmbed(rank, page, user):
    reinforces = rank[page * 15:page * 15 + 15]

    def key(x): return json.loads(x['max'])['value']
    reinforces = sorted(reinforces, key=lambda x : key(x), reverse=True)

    embed = discord.Embed(title='강화 랭킹을 알려드릴게요!', description='랭킹은 최대 강화 수치를 기준으로 해요. 강화 시도 횟수도 같이 알려드릴게요.')
    for idx, r in enumerate(reinforces):
        _max   = json.loads(r['max'])
        _try   = json.loads(r['try'])
        name   = f"> {page * 15 + idx + 1}등"
        if str(user.id) == r['did']:
            name += f"({user.display_name}님)"
        value  = f"+{_max['value']} {_max['itemName']}\r\n"
        value += f"성공 : {_try['success']}회\r\n"
        value += f"실패 : {_try['fail']}회\r\n"
        value += f"파괴 : {_try['destroy']}회"
        embed.add_field(name=name, value=value)
    return embed
