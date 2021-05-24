import discord
import json
from Database import Tool
from Src import DNFAPI, Util

async def 강화(bot, ctx, *inputs):
    def MAKE_EMBED(eReinforce):
        eDid, eName = ctx.author.id, ctx.author.display_name
        eProb, eCost = getReinforceInfo(eReinforce['value'] + 1)

        eEmbed = discord.Embed(title=f"{eName}님의 강화", description=f"강화를 시도하려면 ⭕, 취소하려면 ❌ 이모지를 눌러주세요.")
        eEmbed.add_field(name=f"> 장비", value=f"+{eReinforce['value']} {eReinforce['itemName']}", inline=False)
        eEmbed.add_field(name=f"> 성공 확률", value=f"{eProb}%")
        eEmbed.add_field(name=f"> 소모 골드", value=f"{format(eCost, ',')}골드")
        eEmbed.add_field(name=f"> 보유 골드", value=f"{format(Tool.getGold(eDid), ',')}골드")
        eEmbed.set_thumbnail(url=DNFAPI.getItemImageUrl(eReinforce['itemId']))
        return eEmbed

    def DO_REINFORCE(eReinforce):
        import random
        oldTry = json.loads(eReinforce['try'])
        oldMax = json.loads(eReinforce['max'])
        eProb, eCost = getReinforceInfo(eReinforce['value'] + 1)

        seed = random.randint(1, 100)

        # 성공했을 경우
        if seed <= eProb:
            newValue = eReinforce['value'] + 1
            newTry = {
                'success': oldTry['success'] + 1,
                'fail': oldTry['fail'],
                'destroy': oldTry['destroy']
            }
            newMax = {
                'itemName': eReinforce['itemName'],
                'value': eReinforce['value'] + 1
            } if oldMax['value'] < eReinforce['value'] + 1 else oldMax

            Tool.setReinforce(did, value=newValue, _max=newMax, _try=newTry)
            success = True

        # 실패했을 경우
        else:
            if 0 <= eReinforce['value'] < 10:
                newValue = eReinforce['value']
            elif 10 <= eReinforce['value'] <= 11:
                newValue = eReinforce['value'] - 3
            else:
                newValue = 0

            newTry = {
                'success': oldTry['success'],
                'fail': oldTry['fail'] + 1 if eReinforce['value'] < 12 else oldTry['fail'],
                'destroy': oldTry['destroy'] + 1 if eReinforce['value'] >= 12 else oldTry['destroy']
            }

            Tool.setReinforce(did, value=newValue, _try=newTry)
            success = False

        Tool.gainGold(did, -eCost)
        return success

    did, name = ctx.author.id, ctx.author.display_name
    reinforce = Tool.getReinforce(did)

    # 강화 재설정
    if inputs:
        itemName = ' '.join(inputs)
        itemsInfo = DNFAPI.getItemsInfo(itemName, itemType='무기')
        itemId = await Util.getItemIdFromItemsInfo(bot, ctx, itemsInfo,
                                                   title=f"{name}님의 강화 설정",
                                                   description='강화에 사용할 무기를 선택해주세요. 15초 안에 선택해야해요.',
                                                   footer=f"무기를 선택하면 `+{reinforce['value']} {reinforce['itemName']}`는 사라져요." if reinforce is not None else None,
                                                   skip=False)
        if itemId is None: return

        itemDetailInfo = DNFAPI.getItemDetailInfo(itemId)
        Tool.setReinforce(did, itemId=itemDetailInfo['itemId'], itemName=itemDetailInfo['itemName'], value=0)
        reinforce = Tool.getReinforce(did)

    # 강화설정이 안되어있는 경우
    if reinforce is None:
        embed = discord.Embed(title=f"{name}님의 강화",
                              description='`!강화 <무기아이템이름>` 명령어를 사용해서 강화할 무기를 설정해주세요.\n'
                                          '무기 설정 후에는 `!강화` 명령어를 사용해서 강화를 할 수 있어요.')
        await ctx.channel.send(embed=embed)
        return

    # 계정 생성이 안되어있는 경우
    if Tool.getAccount(did) is None:
        Tool.iniAccount(did)

    embed = MAKE_EMBED(reinforce)
    message = await ctx.channel.send(embed=embed)
    await message.add_reaction('⭕')
    await message.add_reaction('❌')

    while True:
        def check(_reaction, _user):
            return str(_reaction) in ['⭕', '❌'] and _user.id == ctx.author.id and _reaction.message.id == message.id
        reaction, user = await bot.wait_for('reaction_add', check=check)

        # 강화 시도
        if str(reaction) == '⭕':
            prob, cost = getReinforceInfo(reinforce['value'] + 1)

            if Tool.getGold(did) < cost:
                embed.set_footer(text='강화에 필요한 골드가 부족해요.')
            else:
                result = DO_REINFORCE(reinforce)
                reinforce = Tool.getReinforce(did)
                embed = MAKE_EMBED(reinforce)
                if result:
                    embed.set_footer(text='강화에 성공했어요.')
                else:
                    embed.set_footer(text='강화에 실패했어요.')
            await message.edit(embed=embed)
            await message.clear_reactions()
            await message.add_reaction('⭕')
            await message.add_reaction('❌')

        # 강화 취소
        elif str(reaction) == '❌':
            embed.set_footer(text='강화가 취소되었어요.')
            await message.edit(embed=embed)
            await message.clear_reactions()
            return

async def 공개강화(bot, ctx):
    def MAKE_EMBED(eReinforce, eDonationSum, eDonationLog):
        eDid, eName = ctx.author.id, ctx.author.display_name
        eProb, eCost = getReinforceInfo(eReinforce['value'] + 1)

        eEmbed = discord.Embed(title=f"{eName}님의 공개 강화",
                               description=f"강화를 시도하려면 ⭕, 취소하려면 ❌, 기부하려면 ❤️이모지를 눌러주세요.\n"
                                           f"기부한 골드는 회수할 수 없고 강화를 취소하면 기부 골드는 모두 소멸되요.")
        eEmbed.add_field(name=f"> 장비", value=f"+{eReinforce['value']} {eReinforce['itemName']}")
        eEmbed.add_field(name=f"> 성공 확률", value=f"{eProb}%")
        eEmbed.add_field(name=f"> 소모 골드", value=f"{format(eCost, ',')}골드")
        eEmbed.add_field(name=f"> 보유 골드", value=f"{format(Tool.getGold(did), ',')}골드")
        eEmbed.add_field(name=f"> 기부 골드", value=f"{format(eDonationSum, ',')}골드")
        if eDonationLog == {}:
            eEmbed.add_field(name='> 기부 내역', value='없음')
        else:
            eValue = ''
            for index, (k, v) in enumerate(eDonationLog.items()):
                eValue += f"{k}님 : {format(v, ',')}골드\n"
            eEmbed.add_field(name='> 기부 내역', value=eValue)
        eEmbed.set_thumbnail(url=DNFAPI.getItemImageUrl(eReinforce['itemId']))
        return eEmbed

    def DO_REINFORCE(eReinforce, eDonationSum):
        import random
        eDid = ctx.author.id

        oldTry = json.loads(eReinforce['try'])
        oldMax = json.loads(eReinforce['max'])
        eProb, eCost = getReinforceInfo(eReinforce['value'] + 1)

        seed = random.randint(1, 100)

        # 성공했을 경우
        if seed <= eProb:
            newValue = eReinforce['value'] + 1
            newTry = {
                'success': oldTry['success'] + 1,
                'fail': oldTry['fail'],
                'destroy': oldTry['destroy']
            }
            newMax = {
                'itemName': eReinforce['itemName'],
                'value': eReinforce['value'] + 1
            } if oldMax['value'] < eReinforce['value'] + 1 else oldMax

            Tool.setReinforce(eDid, value=newValue, _max=newMax, _try=newTry)
            success = True

        # 실패했을 경우
        else:
            if 0 <= eReinforce['value'] < 10:
                newValue = eReinforce['value']
            elif 10 <= eReinforce['value'] <= 11:
                newValue = eReinforce['value'] - 3
            else:
                newValue = 0

            newTry = {
                'success': oldTry['success'],
                'fail': oldTry['fail'] + 1 if eReinforce['value'] < 12 else oldTry['fail'],
                'destroy': oldTry['destroy'] + 1 if eReinforce['value'] >= 12 else oldTry['destroy']
            }

            Tool.setReinforce(eDid, value=newValue, _try=newTry)
            success = False

        # 기부금이 부족한 경우
        if eDonationSum < eCost:
            eDonationSum = 0
            Tool.gainGold(eDid, eDonationSum - eCost)
        else:
            eDonationSum -= eCost

        return success, eDonationSum

    async def DO_DONATION(eUser):
        eGold = Tool.getGold(eUser.id)
        eEmbed = discord.Embed(title=f"{eUser.display_name}님의 공개 강화 기부",
                               description=f"{ctx.author.display_name}님에게 기부할 골드를 입력해주세요.\n"
                                           f"한번 기부한 골드는 회수할 수 없어요. 신중히 입력해주세요.")
        eEmbed.add_field(name='> 보유 골드', value=f"{format(eGold, ',')}골드")
        eEmbed.set_footer(text='20초 안에 입력해야해요.')
        eMessage = await ctx.channel.send(embed=eEmbed)

        try:
            def eCheck(_message):
                return ctx.channel.id == _message.channel.id and eUser == _message.author
            eAnswer = await bot.wait_for('message', check=eCheck, timeout=20)
            await eAnswer.delete()

            if eGold < int(eAnswer.content):
                eEmbed = discord.Embed(title=f"{eUser.display_name}님의 공개 강화 기부",
                                       description=f"보유 골드보다 많이 기부할 수 없어요. 다시 시도해주세요.")
                await eMessage.edit(embed=eEmbed)
                return False

            elif int(eAnswer.content) <= 0:
                eEmbed = discord.Embed(title=f"{eUser.display_name}님의 공개 강화 기부",
                                       description=f"기부는 1골드 이상만 하실 수 있어요. 다시 시도해주세요.")
                await eMessage.edit(embed=eEmbed)
                return False

            else:
                await eMessage.delete()
                Tool.gainGold(eUser.id, -int(eAnswer.content))
                return int(eAnswer.content)

        except:
            eEmbed = discord.Embed(title=f"{eUser.display_name}님의 공개 강화 기부",
                                   description=f"입력이 잘못되었어요. 다시 시도해주세요.")
            await eMessage.edit(embed=eEmbed)
            return False

    await ctx.message.delete()
    did, name = ctx.author.id, ctx.author.display_name

    # 강화설정이 안되어있는 경우
    reinforce = Tool.getReinforce(did)
    if reinforce is None:
        await ctx.message.delete()
        embed = discord.Embed(title=f"{name}님의 공개 강화",
                              description=f"`!강화 <무기아이템이름>` 명령어를 사용하고 다시 시도해주세요.\n"
                                          f"강화할 무기가 설정되어 있어야 `!공개강화` 명령어를 사용할 수 있어요.")
        await ctx.channel.send(embed=embed)
        return

    # 계정 생성이 안되어있는 경우
    if Tool.getAccount(did) is None:
        Tool.iniAccount(did)

    # 기부금, 기부 로그
    donationSum, donationLog = 0, {}

    embed = MAKE_EMBED(reinforce, donationSum, donationLog)
    message = await ctx.channel.send(embed=embed)
    await message.add_reaction('⭕')
    await message.add_reaction('❌')
    await message.add_reaction('❤️')

    while True:
        def check(_reaction, _user):
            return str(_reaction) in ['⭕', '❌', '❤️'] and _reaction.message.id == message.id and not _user.bot
        reaction, user = await bot.wait_for('reaction_add', check=check)

        # 강화 시도
        if str(reaction) == '⭕' and user.id == did:
            await message.clear_reactions()
            prob, cost = getReinforceInfo(reinforce['value'] + 1)

            if Tool.getGold(did) + donationSum < cost:
                embed.set_footer(text='강화에 필요한 골드가 부족합니다.')
            else:
                result, donationSum = DO_REINFORCE(reinforce, donationSum)
                reinforce = Tool.getReinforce(did)
                embed = MAKE_EMBED(reinforce, donationSum, donationLog)
                if result:
                    embed.set_footer(text='강화에 성공했어요.')
                else:
                    embed.set_footer(text='강화에 실패했어요.')

            await message.edit(embed=embed)
            await message.add_reaction('⭕')
            await message.add_reaction('❌')
            await message.add_reaction('❤️')

        # 강화 취소
        elif str(reaction) == '❌' and user.id == did:
            await message.clear_reactions()
            embed.set_footer(text='공개 강화가 취소되었어요.')
            await message.edit(embed=embed)
            return

        # 도네이션
        elif str(reaction) == '❤️':
            await message.clear_reactions()
            if user.id == did:
                embed.set_footer(text='본인의 공개 강화에는 기부할 수 없어요.')
                await message.edit(embed=embed)
            else:
                if Tool.getAccount(user.id) is None:
                    Tool.iniAccount(user.id)
                embed.set_footer(text=f"{user.display_name}님이 기부를 진행 중이예요...")
                await message.edit(embed=embed)

                donation = await DO_DONATION(user)
                if donation > 0:
                    donationLog.setdefault(user.display_name, 0)
                    donationLog[user.display_name] += donation
                    donationSum += donation

                embed = MAKE_EMBED(reinforce, donationSum, donationLog)
                embed.set_footer(text=f"{user.display_name}님이 {format(donation, ',')}골드를 기부했어요!")
                await message.edit(embed=embed)
            await message.add_reaction('⭕')
            await message.add_reaction('❌')
            await message.add_reaction('❤️')

async def 강화내역(ctx):
    did, name = ctx.author.id, ctx.author.display_name

    # 강화설정이 안되어있는 경우
    reinforce = Tool.getReinforce(did)
    if reinforce is None:
        await ctx.message.delete()
        embed = discord.Embed(title=f"{name}님의 강화 정보",
                              description=f"`!강화 '무기아이템이름'` 명령어를 사용하고 다시 시도해주세요.\n"
                                          f"강화할 무기가 설정되어 있어야 `!공개강화` 명령어를 사용할 수 있어요.")
        await ctx.channel.send(embed=embed)
        return

    _max = json.loads(reinforce['max'])
    _try = json.loads(reinforce['try'])

    await ctx.message.delete()
    embed = discord.Embed(title=f"{name}님의 강화 정보를 알려드릴게요.")
    embed.add_field(name=f"> 현재 장비", value=f"+{reinforce['value']} {reinforce['itemName']}")
    embed.add_field(name=f"> 최고 강화 수치", value=f"+{_max['value']} {_max['itemName']}")
    embed.add_field(name=f"> 강화 시도", value=f"성공 : {format(_try['success'], ',')}회\n"
                                               f"실패 : {format(_try['fail'], ',')}회\n"
                                               f"파괴 : {format(_try['destroy'], ',')}회")
    embed.set_thumbnail(url=DNFAPI.getItemImageUrl(reinforce['itemId']))
    await ctx.channel.send(embed=embed)

async def 강화랭킹(bot, ctx):
    def MAKE_EMBED(eReinforces, ePage):
        def key(x): return json.loads(x['max'])['value']

        eReinforces = sorted(eReinforces, key=lambda x: key(x), reverse=True)
        eReinforces = eReinforces[ePage * 15:ePage * 15 + 15]

        eEmbed = discord.Embed(title='강화 랭킹을 알려드릴게요!', description='강화 랭킹은 최대 강화 수치를 기준으로 해요.')
        for idx, eReinforce in enumerate(eReinforces):
            _max = json.loads(eReinforce['max'])
            _try = json.loads(eReinforce['try'])

            eName = f"> {ePage * 15 + idx + 1}등"
            if str(ctx.author.id) == eReinforce['did']:
                eName += f"({ctx.author.display_name}님)"
            eValue = f"+{_max['value']} {_max['itemName']}\n" \
                     f"성공 : {_try['success']}회\n" \
                     f"실패 : {_try['fail']}회\n" \
                     f"파괴 : {_try['destroy']}회"
            eEmbed.add_field(name=eName, value=eValue)
            eEmbed.set_footer(text=f"{ePage + 1}페이지 / {(len(eReinforces) - 1) // 15 + 1}페이지")
        return eEmbed

    await ctx.message.delete()
    message = await ctx.channel.send('> 강화 랭킹을 불러오는 중이예요...')

    reinforces = Tool.getReinforces()
    embed = MAKE_EMBED(reinforces, 0)
    await message.edit(embed=embed, content=None)
    if len(reinforces) > 15: await message.add_reaction('▶️')

    page = 0
    while len(reinforces) > 15:
        def check(_reaction, _user):
            return str(_reaction) in ['◀️', '▶️'] and _user.id == ctx.author.id and _reaction.message.id == message.id
        reaction, user = await bot.wait_for('reaction_add', check=check)

        if str(reaction) == '◀️' and page > 0:
            page -= 1
        if str(reaction) == '▶️' and page < (len(reinforces) - 1) // 15:
            page += 1

        embed = MAKE_EMBED(reinforces, page)
        await message.edit(embed=embed)
        await message.clear_reactions()
        if page > 0:
            await message.add_reaction('◀️')
        if page < (len(reinforces) - 1) // 15:
            await message.add_reaction('▶️')

def getReinforceInfo(value):
    info = {
        1:  (100, 354600),
        2:  (100, 354600),
        3:  (100, 354600),
        4:  (100, 354600),
        5:  (80, 709200),
        6:  (70, 780120),
        7:  (60, 851040),
        8:  (50, 921960),
        9:  (40, 992880),
        10: (30, 1063800),
        11: (25, 1063800),
        12: (18, 1773000),
        13: (17, 2836800),
        14: (16, 4255200),
        15: (14, 6028200)
    }
    return info[value]
