import json
import discord
from src.adv import item
from database import connection, tool

async def 모험(ctx):
    adv = tool.getAdventure(ctx.message.author.id)
    if adv is None:
        tool.iniAdventure(ctx.message.author.id)
        adv = tool.getAdventure(ctx.message.author.id)

    equipment = tool.getEquipment(ctx.message.author.id)
    embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 모험 정보를 알려드릴게요.')
    embed.add_field(name='> 직업', value=getJobName(adv['job']))
    embed.add_field(name='> 레벨',     value=getLevelInfo(adv['level']))
    embed.add_field(name='> 경험치',   value=getExpInfo(adv['level'], adv['exp']))
    embed.add_field(name='> 능력치', value=getPlayerStatInfo(adv), inline=False)
    embed.add_field(name='> 무기',     value=item.getItemInfo(equipment['weapon']))
    embed.add_field(name='> 악세서리', value=item.getItemInfo(equipment['accessory']))
    embed.add_field(name='> 추가장비', value=item.getItemInfo(equipment['additional']))
    await ctx.message.delete()
    await ctx.channel.send(embed=embed)

async def 직업(bot, ctx):
    adv = tool.getAdventure(ctx.message.author.id)
    embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 직업 선택",
                          description=f"원하시는 직업을 입력해주세요. 현재 직업은 `{getJobName(adv['job'])}` 입니다.")
    embed.add_field(name='> 귀검사', value='기본 공격을 주로 사용하는 직업군. 대검, 소검, 둔기, 도, 광검을 사용하며 밸런스있는 스탯을 가집니다.')
    embed.add_field(name='> 마법사', value='스킬 공격을 주로 사용하는 직업군. 창, 봉, 로드, 스탭, 빗자루를 사용하며 체력이 적고 마력이 높습니다.')
    await ctx.message.delete()
    msg = await ctx.channel.send(embed=embed)

    try:
        def check(_message):
            return ctx.channel.id == _message.channel.id and ctx.message.author == _message.author
        response = await bot.wait_for('message', check=check)
        if response.content in ['귀검사', '마법사']:
            embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 직업 선택",
                                  description=f"`{response.content}` 를 선택하셨습니다.\r\n진행하시려면 ⭕, 취소하려면 ❌ 이모지를 추가해주세요.")
            if adv['job'] != 0:
                embed.set_footer(text=f"경고 :: 이미 직업을 갖고있어요! 만약 새로운 직업을 선택한다면 모든 데이터가 초기화되요.")
            await response.delete()
            await msg.edit(embed=embed)
            await msg.add_reaction('⭕')
            await msg.add_reaction('❌')

            try:
                def _check(_reaction, _user):
                    return str(_reaction) in ['⭕', '❌'] and _user == ctx.author and _reaction.message.id == msg.id
                reaction, user = await bot.wait_for('reaction_add', check=_check)
                if str(reaction) == '⭕':
                    tool.changeJob(ctx.message.author.id, jobName=response.content)
                    embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 직업 선택",
                                          description=f"`{response.content}`로 성공적으로 전직했습니다!")
                    await msg.clear_reactions()
                    await msg.edit(embed=embed)
                else:
                    embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 직업 선택",
                                          description='직업 선택이 취소되었습니다. 다시 시도해주세요.')
                    await msg.clear_reactions()
                    await msg.edit(embed=embed)
            except: pass
        else:
            embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 직업 선택",
                                  description=f"입력이 잘못되었어요. 다시 시도해주세요.")
            await response.delete()
            await msg.edit(embed=embed)
    except: pass

async def 장비뽑기(bot, ctx):
    if not isValid(ctx.message.author.id):
        await ctx.message.delete()
        embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 장비 뽑기',
                              description='`!주식` 또는 `!모험` 명령어를 사용한 후에 다시 시도해주세요.\r\n'
                                          '두 가지 명령어를 적어도 한 번씩은 사용한 적이 있어야합니다.')
        await ctx.channel.send(embed=embed)
        return

    gold = tool.getGold(ctx.message.author.id)
    embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 장비 뽑기',
                          description='과도한 뽑기는 정신건강에 영향을 줄 수도 있어요.')
    embed.add_field(name='> 보유 금액', value=f"{format(gold, ',')}골드")
    embed.add_field(name='> 3회 뽑기',  value=f"300,000골드")
    embed.add_field(name='> 9회 뽑기',  value=f"900,000골드")

    await ctx.message.delete()
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('3️⃣')
    await msg.add_reaction('9️⃣')

    try:
        def check(reaction, user):
            return (str(reaction) == '3️⃣' or str(reaction) == '9️⃣') \
                   and user == ctx.author and reaction.message.id == msg.id
        reaction, user = await bot.wait_for('reaction_add', check=check)
        if str(reaction) == '3️⃣':
            await msg.delete()
            await item.doGacha(bot, ctx, 3)
        elif str(reaction) == '9️⃣':
            await msg.delete()
            await item.doGacha(bot, ctx, 9)
    except Exception as e:
        await ctx.channel.send(f'{e}')
        return

async def 인벤토리(bot, ctx):
    if not isValid(ctx.message.author.id):
        await ctx.message.delete()
        embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 장비 뽑기',
                              description='`!주식` 또는 `!모험` 명령어를 사용한 후에 다시 시도해주세요.\r\n'
                                          '두 가지 명령어를 적어도 한 번씩은 사용한 적이 있어야합니다.')
        await ctx.channel.send(embed=embed)
        return

    inv = tool.getInventory(ctx.message.author.id)
    if inv is None:
        embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 모험 인벤토리를 보여드릴게요.",
                              description=f"인벤토리에 아이템이 없어요! `!모험뽑기` 를 통해서 아이템을 획득해보세요.")
        await ctx.message.delete()
        await ctx.channel.send(embed=embed)
        return

    await ctx.message.delete()
    selection = await getInventorySelection(bot, ctx, inv, 0)
    if selection != -1: await item.setEquipItem(bot, ctx, inv, selection)

async def 강화(bot, ctx):
    did, name = ctx.message.author.id, ctx.message.author.display_name
    if not isValid(did):
        await ctx.message.delete()
        embed = discord.Embed(title=f'{name}님의 장비 강화',
                              description='`!주식` 또는 `!모험` 명령어를 사용한 후에 다시 시도해주세요.\r\n'
                                          '두 가지 명령어를 적어도 한 번씩은 사용한 적이 있어야합니다.')
        await ctx.channel.send(embed=embed)
        return

    equipment = tool.getEquipment(did)
    if not equipment['weapon'] and not equipment['accessory'] and not equipment['additional']:
        await ctx.message.delete()
        embed = discord.Embed(title=f'{name}님의 장비 강화',
                              description='장착하고 있는 장비가 없어요. `!인벤토리` 명령어로 장비를 장착할 수 있어요.')
        await ctx.channel.send(embed=embed)
        return

    embed = discord.Embed(title=f'{name}님의 장비 강화', description='강화하고 싶은 장비를 선택해주세요.')
    embed.add_field(name='> 무기',     value=item.getItemInfo(equipment['weapon']))
    embed.add_field(name='> 악세서리', value=item.getItemInfo(equipment['accessory']))
    embed.add_field(name='> 추가장비', value=item.getItemInfo(equipment['additional']))
    await ctx.message.delete()
    msg = await ctx.channel.send(embed=embed)
    if equipment['weapon']:     await msg.add_reaction('1️⃣')
    if equipment['accessory']:  await msg.add_reaction('2️⃣')
    if equipment['additional']: await msg.add_reaction('3️⃣')
    await item.reinforceConfirm(bot, ctx, equipment, msg)

# 판별
def isValid(did):
    try:
        conn, cur = connection.getConnection()
        sql = f'SELECT * FROM stock WHERE did={did}'
        cur.execute(sql)
        stock = cur.fetchone()

        sql = f'SELECT * FROM adventure WHERE did={did}'
        cur.execute(sql)
        adventure = cur.fetchone()
    except: return False

    if stock is not None and adventure is not None:
        return True
    else:
        return False

# 게터
def getJobName(job):
    if job is None:  return '모험가'
    elif job == 0  : return '모험가'
    elif job == 100: return '귀검사'
    elif job == 200: return '격투가'
    elif job == 300: return '거너'
    elif job == 400: return '마법사'

def getLevelInfo(level):
    return f'{level}레벨'

def getExpInfo(level, exp):
    expTable = {
        1 : 10,
        2 : 15,
        3 : 20,
        4 : 30,
        5 : 50
    }
    _exp = format(exp, ',')
    _tot = format(expTable[level], ',')
    _per = format(exp / expTable[level] * 100, '.2f')
    return f"{_per}% ({_exp} / {_tot})"

def getStat(adventure):
    options = {
        '공격력' : adventure['ap'],
        '방어력' : adventure['def'],
        '스탯'   : adventure['stat'],
        '체력'   : adventure['maxhp'],
        '마력'   : adventure['maxmp'],
        '크리티컬 확률' : 5,
        '추가 데미지'   : 0,
        '데미지 증가'   : 0,
        '크리티컬 데미지 증가' : 0
    }
    return options

def getPlayerStatInfo(adventure):
    equipment = json.loads(adventure['equipment'])
    options = getStat(adventure)
    for i in equipment:
        try:
            for j in equipment[i]['option']:
                if j in options.keys():
                    options[j] += equipment[i]['option'][j]
        except: pass

    desc =  f"공격력 : {options['공격력']} | 스탯 : {options['스탯']} | 방어력 : {options['방어력']} | "
    desc += f"체력   : {options['체력']}   | 마력 : {options['마력']} | 크리티컬 확률 : {options['크리티컬 확률']}%\r\n"
    desc += f"추가 데미지 : {options['추가 데미지']}% | 데미지 증가 : {options['데미지 증가']}% | 크리티컬 데미지 증가 : {options['크리티컬 데미지 증가']}%"
    return desc

async def getInventorySelection(bot, ctx, inv, page, title=None, description=None, msg=None):
    if len(inv) == 0:
        embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 모험 인벤토리를 보여드릴게요.",
                              description='인벤토리가 비어있어요. `!장비뽑기`로 아이템을 획득해보세요!')
        await ctx.channel.send(embed=embed)
        return -1

    _inv = inv[page * 9 : page * 9 + 9]
    if title is not None and description is not None:
        embed = discord.Embed(title=title, description=description)
    else:
        embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 모험 인벤토리를 보여드릴게요.",
                              description=f"장착할 아이템의 번호와 동일한 이모지를 추가해주세요.")

    for index, _item in enumerate(_inv):
        embed.add_field(name=f"> {index + 1}", value=item.getItemInfo(_item))
    embed.set_footer(text=f'{(len(inv) - 1) // 9 + 1}쪽 중 {page + 1}쪽')

    if msg is None:
        msg = await ctx.channel.send(embed=embed)
    else:
        await msg.edit(embed=embed)

    if page > 0: await msg.add_reaction('◀️')
    if len(_inv) >= 1: await msg.add_reaction('1️⃣')
    if len(_inv) >= 2: await msg.add_reaction('2️⃣')
    if len(_inv) >= 3: await msg.add_reaction('3️⃣')
    if len(_inv) >= 4: await msg.add_reaction('4️⃣')
    if len(_inv) >= 5: await msg.add_reaction('5️⃣')
    if len(_inv) >= 6: await msg.add_reaction('6️⃣')
    if len(_inv) >= 7: await msg.add_reaction('7️⃣')
    if len(_inv) >= 8: await msg.add_reaction('8️⃣')
    if len(_inv) >= 9: await msg.add_reaction('9️⃣')
    if page < (len(inv) - 1) // 9: await msg.add_reaction('▶️')

    while True:
        try:
            def check(reaction, user):
                return str(reaction) in ['◀️', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '▶️'] \
                       and user == ctx.author and reaction.message.id == msg.id
            reaction, user = await bot.wait_for('reaction_add', check=check)
            if str(reaction) == '◀️' and page > 0:
                page -= 1
            if str(reaction) == '▶️' and page < (len(inv) - 1) // 9:
                page += 1
            if str(reaction) in ['◀️', '▶️']:
                await msg.clear_reactions()
                selection = await getInventorySelection(bot, ctx, inv, page, title, description, msg)
                return selection
            elif str(reaction) == '1️⃣':
                await msg.delete()
                return page * 9
            elif str(reaction) == '2️⃣':
                await msg.delete()
                return page * 9 + 1
            elif str(reaction) == '3️⃣':
                await msg.delete()
                return page * 9 + 2
            elif str(reaction) == '4️⃣':
                await msg.delete()
                return page * 9 + 3
            elif str(reaction) == '5️⃣':
                await msg.delete()
                return page * 9 + 4
            elif str(reaction) == '6️⃣':
                await msg.delete()
                return page * 9 + 5
            elif str(reaction) == '7️⃣':
                await msg.delete()
                return page * 9 + 6
            elif str(reaction) == '8️⃣':
                await msg.delete()
                return page * 9 + 7
            elif str(reaction) == '9️⃣':
                await msg.delete()
                return page * 9 + 8
        except Exception as e:
            return -1