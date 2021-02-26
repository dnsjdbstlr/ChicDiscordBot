import json
import discord
from src.adv import item
from database import connection, tool

async def 모험(ctx):
    adv = tool.getAdventure(ctx.message.author.id)
    if adv is None:
        iniAdventure(ctx.message.author.id)
        adv = tool.getAdventure(ctx.message.author.id)

    equipment = tool.getEquipment(ctx.message.author.id)
    embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 모험 정보를 알려드릴게요.')
    embed.add_field(name='> 직업',     value=getJobInfo(adv['job']))
    embed.add_field(name='> 레벨',     value=getLevelInfo(adv['level']))
    embed.add_field(name='> 경험치',   value=getExpInfo(adv['level'], adv['exp']))
    embed.add_field(name='> 능력치',   value=getStatInfo(adv), inline=False)
    embed.add_field(name='> 무기',     value=getItemInfo(equipment['weapon']))
    embed.add_field(name='> 악세서리', value=getItemInfo(equipment['accessory']))
    embed.add_field(name='> 추가장비', value=getItemInfo(equipment['additional']))
    await ctx.message.delete()
    await ctx.channel.send(embed=embed)

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
            await gacha(bot, ctx, 3)
        elif str(reaction) == '9️⃣':
            await msg.delete()
            await gacha(bot, ctx, 9)
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
    if selection != -1: await setEquipItem(bot, ctx, inv, selection)

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
    embed = discord.Embed(title=f'{name}님의 장비 강화', description='강화하고 싶은 장비를 선택해주세요.')
    embed.add_field(name='> 무기',     value=getItemInfo(equipment['weapon']))
    embed.add_field(name='> 악세서리', value=getItemInfo(equipment['accessory']))
    embed.add_field(name='> 추가장비', value=getItemInfo(equipment['additional']))
    await ctx.message.delete()
    msg = await ctx.channel.send(embed=embed)
    if equipment['weapon']:     await msg.add_reaction('1️⃣')
    if equipment['accessory']:  await msg.add_reaction('2️⃣')
    if equipment['additional']: await msg.add_reaction('3️⃣')

    try:
        await reinforceConfirm(bot, ctx, equipment, msg)
    except: pass

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

# 세팅
def iniAdventure(did):
    conn, cur = connection.getConnection()
    inventory = {'inventory': []}
    equipment = {'weapon': [], 'accessory': [], 'additional': []}
    sql = 'INSERT INTO adventure values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    cur.execute(sql, (did, 0, 1, 0, 5, 0, 0, 50, 50, json.dumps(inventory), json.dumps(equipment)))
    conn.commit()

def createItem(itemId):
    if itemId // 10000 == 1:
        return item.WEAPON.get(str(itemId))
    elif itemId // 10000 == 2:
        return item.ACCESSORY.get(str(itemId))
    else:
        return None

# 게터
def getJobInfo(job):
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
        3 : 20
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

def getStatInfo(adventure):
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

def getItemInfo(item):
    try:
        # 이름
        if item['info']['reinforce'] > 0:
            desc = f"+{item['info']['reinforce']} "
        else:
            desc = ''
        desc += f"{item['info']['name']}\r\n"

        # 타입
        if item['info']['id'] // 10000 == 1:
            desc += f"타입 : {item['info']['rarity']} {getWeaponType(item['info']['id'])}\r\n"
        elif item['info']['id'] // 10000 == 2:
            desc += f"타입 : {item['info']['rarity']} 악세서리\r\n"
        elif item['info']['id'] // 10000 == 3:
            desc += f"타입 : {item['info']['rarity']} 추가장비\r\n"

        # +옵션
        reinforceStat = getReinforceStat(item)
        for option in ['공격력', '스탯', '체력', '마력', '방어력']:
            temp = item['option'].get(option)
            if temp is None: continue

            desc += f"{option} : {temp}"
            if item['info']['reinforce'] > 0 and reinforceStat.get(option) is not None:
                if temp is None:
                    desc += f"{option} : 0(+{reinforceStat.get(option)})\r\n"
                else:
                    desc += f"(+{reinforceStat.get(option)})\r\n"
            else:
                desc += '\r\n'
        
        # %옵션
        for option in ['크리티컬 확률', '추가 데미지', '데미지 증가', '크리티컬 데미지 증가']:
            temp = item['option'].get(option)
            if temp is None: continue
            desc += f"{option} : {temp}%\r\n"
        return desc
    except:
        return '없음'

def getItemType(itemId):
    typeId = itemId // 10000
    if typeId == 1:
        return 'weapon'
    if typeId == 2:
        return 'accessory'
    if typeId == 3:
        return 'additional'
    return 'err'

def getWeaponType(itemId):
    if itemId // 10000 != 1:
        return '오류'
    itemId %= 10000

    # 귀검사
    if itemId // 100 == 0:
        return '대검'
    if itemId // 100 == 1:
        return '소검'
    if itemId // 100 == 2:
        return '둔기'
    if itemId // 100 == 3:
        return '도'
    if itemId // 100 == 4:
        return '광검'

    # 마법사
    if itemId // 100 == 10:
        return '창'
    if itemId // 100 == 11:
        return '봉'
    if itemId // 100 == 12:
        return '로드'
    if itemId // 100 == 13:
        return '스탭'
    if itemId // 100 == 14:
        return '빗자루'

def getGachaReward(count):
    reward = []

    import random
    for i in range(count):
        part = random.choice(['weapon', 'accessory'])
        if part == 'weapon':
            legendary = [10000, 10100, 10200, 10300, 10400]
            epic      = []
            mythic    = []

        elif part == 'accessory':
            legendary = [20000, 20001, 20002]

        seed = random.randint(1, 100)
        if 1 <= seed <= 100:
            itemId = random.choice(legendary)
        reward.append(createItem(itemId))

    return reward

def getReinforceProb(reinforce):
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
    return prob[reinforce]

def getReinforceCost(reinforce, _type):
    weapon_cost = {
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
    cost = {
        1 : 295500,
        2 : 295500,
        3 : 295500,
        4 : 295500,
        5 : 591000,
        6 : 650100,
        7 : 709200,
        8 : 768300,
        9 : 827400,
        10 : 886500,
        11 : 886500,
        12 : 1477500,
        13 : 2364000,
        14 : 3546000,
        15 : 5023500
    }

    if _type == 'weapon':
        return weapon_cost[reinforce]
    else:
        return cost[reinforce]

def getReinforceStat(item):
    _type = getItemType(item['info']['id'])
    weapon_stat = {
        1 : {'공격력' : 10, '스탯' : 1},
        2 : {'공격력' : 20, '스탯' : 2},
        3 : {'공격력' : 30, '스탯' : 3},
        4 : {'공격력' : 40, '스탯' : 4},
        5 : {'공격력' : 60, '스탯' : 5},
        6 : {'공격력' : 80, '스탯' : 6},
        7 : {'공격력' : 100, '스탯' : 7},
        8 : {'공격력' : 120, '스탯' : 8},
        9 : {'공격력' : 140, '스탯' : 9},
        10 : {'공격력' : 160, '스탯' : 10},
        11 : {'공격력' : 200, '스탯' : 15},
        12 : {'공격력' : 250, '스탯' : 20},
        13 : {'공격력' : 300, '스탯' : 30},
        14 : {'공격력' : 400, '스탯' : 40},
        15 : {'공격력' : 600, '스탯' : 50}
    }

    accessory_stat = {
        1: {'스탯': 5},
        2: {'스탯': 10},
        3: {'스탯': 15},
        4: {'스탯': 20},
        5: {'스탯': 25},
        6: {'스탯': 30},
        7: {'스탯': 35},
        8: {'스탯': 40},
        9: {'스탯': 45},
        10: {'스탯': 50},
        11: {'스탯': 65},
        12: {'스탯': 90},
        13: {'스탯': 130},
        14: {'스탯': 180},
        15: {'스탯': 230}
    }

    additional_stat = {
        1: {'체력' : 10, '마력' : 10, '스탯': 3},
        2: {'체력' : 20, '마력' : 20, '스탯': 6},
        3: {'체력' : 30, '마력' : 30, '스탯': 9},
        4: {'체력' : 40, '마력' : 40, '스탯': 12},
        5: {'체력' : 55, '마력' : 55, '스탯': 15},
        6: {'체력' : 70, '마력' : 70, '스탯': 18},
        7: {'체력' : 85, '마력' : 85, '스탯': 21},
        8: {'체력' : 100, '마력' : 100, '스탯': 24},
        9: {'체력' : 115, '마력' : 115, '스탯': 27},
        10: {'체력' : 130, '마력' : 130, '스탯': 30},
        11: {'체력' : 150, '마력' : 150, '스탯': 40},
        12: {'체력' : 170, '마력' : 170, '스탯': 50},
        13: {'체력' : 200, '마력' : 200, '스탯': 70},
        14: {'체력' : 250, '마력' : 250, '스탯': 100},
        15: {'체력' : 350, '마력' : 350, '스탯': 150},
    }

    try:
        if _type == 'weapon':     return weapon_stat[item['info']['reinforce']]
        if _type == 'accessory':  return accessory_stat[item['info']['reinforce']]
        if _type == 'additional': return additional_stat[item['info']['reinforce']]
        else: return None
    except:
        return None

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

    for index, item in enumerate(_inv):
        embed.add_field(name=f"> {index + 1}", value=getItemInfo(item))
    embed.set_footer(text=f'{(len(inv) - 1) // 9 + 1}쪽 중 {page + 1}쪽')

    if msg is None:
        msg = await ctx.channel.send(embed=embed)
    else:
        await msg.edit(embed=embed)

    if page > 0:
        await msg.add_reaction('◀️')
    if len(_inv) >= 1: await msg.add_reaction('1️⃣')
    if len(_inv) >= 2: await msg.add_reaction('2️⃣')
    if len(_inv) >= 3: await msg.add_reaction('3️⃣')
    if len(_inv) >= 4: await msg.add_reaction('4️⃣')
    if len(_inv) >= 5: await msg.add_reaction('5️⃣')
    if len(_inv) >= 6: await msg.add_reaction('6️⃣')
    if len(_inv) >= 7: await msg.add_reaction('7️⃣')
    if len(_inv) >= 8: await msg.add_reaction('8️⃣')
    if len(_inv) >= 9: await msg.add_reaction('9️⃣')
    if page < (len(inv) - 1) // 9:
        await msg.add_reaction('▶️')

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

async def gacha(bot, ctx, count):
    did = ctx.message.author.id

    try:
        gold = tool.getGold(did)
        if gold - (100000 * count) < 0:
            await ctx.channel.send(f'> 뽑기에 필요한 골드가 부족합니다.')
            return

        inv = tool.getInventory(did)
        if inv is not None and len(inv) + count > 45:
            await ctx.channel.send(f'> 인벤토리 공간이 부족합니다.')
            return
    except Exception as e:
        await ctx.channel.send(f'> 뽑기에 실패했습니다.\r\n> {e}')
        return

    # 뽑기 실행 및 저장
    reward = getGachaReward(count)
    tool.gainItem(did, *reward)
    tool.gainGold(did, -100000 * count)

    embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 모험 뽑기 결과')
    for index, i in enumerate(reward):
        embed.add_field(name=f"> {index + 1}", value=getItemInfo(i))
    embed.set_footer(text=f'🔁 이모지를 추가하면 {count}번 뽑기를 진행합니다.')
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('🔄')

    while True:
        try:
            def check(_reaction, _user):
                return str(_reaction) == '🔄' and _user == ctx.author and _reaction.message.id == msg.id
            reaction, user = await bot.wait_for('reaction_add', check=check)
            await msg.delete()
            await gacha(bot, ctx, count)
        except: pass

async def setEquipItem(bot, ctx, inv, index):
    equipment = tool.getEquipment(ctx.message.author.id)
    _type = getItemType(inv[index]['info']['id'])
    old_equip = equipment.get(_type)
    new_equip = inv[index]

    embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 장비 착용",
                          description='장착되어있는 장비는 사라져요. 선택한 장비를 착용할까요?')
    embed.add_field(name='> 기존 장비', value=getItemInfo(old_equip))
    embed.add_field(name='> 장착 장비', value=getItemInfo(new_equip))
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('⭕')
    await msg.add_reaction('❌')

    try:
        def check(reaction, user):
            return (str(reaction) == '⭕' or str(reaction) == '❌') \
                   and user == ctx.author and reaction.message.id == msg.id
        reaction, user = await bot.wait_for('reaction_add', check=check)
        if str(reaction) == '⭕':
            tool.setEquipment(ctx.message.author.id, new_equip)
            tool.removeItem(ctx.message.author.id, index, inv=inv)

            await msg.delete()
            embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 장비 착용",
                                  description=f"'{new_equip['info']['name']}' 을(를) 성공적으로 장착했습니다.")
            await ctx.channel.send(embed=embed)
        elif str(reaction) == '❌':
            await msg.delete()
            embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 장비 착용",
                                  description=f"장비 착용을 취소했습니다. 더 고민해보고 다시 시도해주세요.")
            await ctx.channel.send(embed=embed)
    except: pass

async def reinforceConfirm(bot, ctx, equipment, msg):
    def check(_reaction, _user):
        return str(_reaction) in ['1️⃣', '2️⃣', '3️⃣'] and _user == ctx.author and _reaction.message.id == msg.id
    reaction, user = await bot.wait_for('reaction_add', check=check)

    if str(reaction) == '1️⃣':
        target = equipment['weapon']
    elif str(reaction) == '2️⃣':
        target = equipment['accessory']
    elif str(reaction) == '3️⃣':
        target = equipment['additional']
    else: return

    prob = getReinforceProb(target['info']['reinforce'] + 1)
    cost = getReinforceCost(target['info']['reinforce'] + 1, getItemType(target['info']['id']))

    await msg.delete()
    embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 장비 강화',
                          description='강화를 시도하려면 O, 취소하려면 X 이모지를 추가해주세요.')
    embed.add_field(name='> 선택한 장비', value=f"+{target['info']['reinforce']} {target['info']['name']}")
    embed.add_field(name='> 성공 확률', value=f"{prob}%")
    embed.add_field(name='> 강화 비용', value=f"{format(cost, ',')}골드")
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('⭕')
    await msg.add_reaction('❌')

    try:
        def _check(__reaction, __user):
            return str(__reaction) in ['⭕', '❌'] and __user == ctx.author and __reaction.message.id == msg.id
        reaction, user = await bot.wait_for('reaction_add', check=_check)
        if str(reaction) == '⭕':
            await msg.delete()
            await reinforce(bot, ctx, target)
        elif str(reaction) == '❌':
            await msg.delete()
            embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 장비 강화',
                                  description='강화가 취소되었습니다. 다시 한번 생각해보고 시도해주세요.')
            await ctx.channel.send(embed=embed)
    except: pass

async def reinforce(bot, ctx, target):
    prob = getReinforceProb(target['info']['reinforce'] + 1)
    cost = getReinforceCost(target['info']['reinforce'] + 1, getItemType(target['info']['id']))
    gold = tool.getGold(ctx.message.author.id)
    if gold < cost:
        embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 장비 강화',
                              description='강화에 필요한 골드가 부족합니다.')
        embed.add_field(name='> 장비', value=f"+{target['info']['reinforce']} {target['info']['name']}")
        embed.add_field(name='> 보유 골드', value=f"{format(gold, ',')}골드")
        embed.add_field(name='> 강화 비용', value=f"{format(cost, ',')}골드")
        await ctx.channel.send(embed=embed)
        return

    tool.gainGold(ctx.message.author.id, -cost)

    import random
    seed = random.randint(1, 100)
    embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 장비 강화')
    if seed <= prob:
        target['info']['reinforce'] += 1
        tool.setEquipment(ctx.message.author.id, target)
        embed.add_field(name='> 결과', value='성공', inline=False)
    else:
        embed.add_field(name='> 결과', value='실패', inline=False)
    embed.add_field(name='> 장비', value=f"+{target['info']['reinforce']} {target['info']['name']}")
    embed.add_field(name='> 보유 골드', value=f"{format(gold - cost, ',')}골드")
    embed.add_field(name='> 강화 비용', value=f"{format(cost, ',')}골드")
    embed.set_footer(text=f"⚔️이모지를 추가하면 다시 강화를 시도합니다. (성공 확률 : {getReinforceProb(target['info']['reinforce'] + 1)}%)")
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('⚔️')

    try:
        def check(_reaction, _user):
            return str(_reaction) == '⚔️' and _user == ctx.author and _reaction.message.id == msg.id
        reaction, user = await bot.wait_for('reaction_add', check=check)
        await msg.delete()
        await reinforce(bot, ctx, target)
    except: pass