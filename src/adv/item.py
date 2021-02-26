"""
무기 :: 10000번대
    귀검사
    대검 :: 10000번대
    소검 :: 10100번대
    둔기 :: 10200번대
    도   :: 10300번대
    광검 :: 10400번대

    마법사
    창     :: 11000번대
    봉     :: 11100번대
    로드   :: 11200번대
    스탭   :: 11300번대
    빗자루 :: 11400번대
"""

import json
import discord
from database import tool

with open('src/adv/weapon.json', 'r', encoding='UTF8') as f:
    WEAPON = json.load(f)

with open('src/adv/accessory.json', 'r', encoding='UTF8') as f:
    ACCESSORY = json.load(f)

def getJobName(job):
    if job is None:  return '모험가'
    elif job == 0  : return '모험가'
    elif job == 100: return '귀검사'
    elif job == 200: return '격투가'
    elif job == 300: return '거너'
    elif job == 400: return '마법사'

def getItem(itemId):
    if itemId // 10000 == 1:
        return WEAPON.get(str(itemId))
    elif itemId // 10000 == 2:
        return ACCESSORY.get(str(itemId))
    else:
        return None

def getItemInfo(item):
    try:
        # 이름
        if item['reinforce']['value'] > 0:
            desc = f"+{item['reinforce']['value']} "
        else:
            desc = ''
        desc += f"{item['name']}\r\n"

        # 타입
        if item['id'] // 10000 == 1:
            desc += f"타입 : {item['rarity']} {getWeaponType(item)}({item['requireClass']})\r\n"
        elif item['id'] // 10000 == 2:
            desc += f"타입 : {item['rarity']} 악세서리\r\n"
        elif item['id'] // 10000 == 3:
            desc += f"타입 : {item['rarity']} 추가장비\r\n"

        # 레벨제한
        desc += f"레벨 제한 : {item['requireLv']}\r\n"

        # +옵션
        for option in ['공격력', '스탯', '체력', '마력', '방어력']:
            temp = item['option'].get(option)

            # 강화 옵션 표기
            if item['reinforce']['value'] > 0 and item['reinforce'].get(option) is not None:
                if temp is None:
                    desc += f"{option} : 0(+{item['reinforce'].get(option)})\r\n"
                else:
                    desc += f"{option} : {temp}(+{item['reinforce'].get(option)})\r\n"
            # 강화 없을 경우
            elif temp is not None:
                desc += f"{option} : {temp}\r\n"

        # %옵션
        for option in ['크리티컬 확률', '추가 데미지', '데미지 증가', '크리티컬 데미지 증가']:
            temp = item['option'].get(option)
            if temp is None: continue
            desc += f"{option} : {temp}%\r\n"
        return desc
    except:
        return '없음'

def getItemType(item):
    _type = item['id'] // 10000
    if _type == 1:
        return 'weapon'
    if _type == 2:
        return 'accessory'
    if _type == 3:
        return 'additional'
    return 'err'

def getWeaponType(item):
    itemId = item['id']
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

async def doGacha(bot, ctx, count):
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
            await doGacha(bot, ctx, count)
        except: pass

def getGachaReward(count):
    reward = []

    import random
    for i in range(count):
        part = random.choice(['weapon', 'accessory'])
        if part == 'weapon':
            legendary = [10000]
            epic      = []
            mythic    = []
        elif part == 'accessory':
            legendary = [20000]
            epic      = []
            mythic    = []
        else:
            legendary = [30000]
            epic      = []
            mythic    = []
        seed = random.randint(1, 100)
        if 1 <= seed <= 100:
            itemId = random.choice(legendary)
        elif 0 <= seed <= 0:
            itemId = 0
        else:
            itemId = 0
        reward.append(getItem(itemId))
    return reward

async def setEquipItem(bot, ctx, inv, index):
    new_equip = inv[index]

    # 착용 조건 검사
    adv = tool.getAdventure(ctx.message.author.id)
    if  adv['level'] < new_equip['requireLv'] or \
        (new_equip['requireClass'] is not None and getJobName(adv['job']) != new_equip['requireClass']):
        embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 장비 착용",
                              description='해당 장비를 장착할 수 없습니다.\r\n레벨이 부족하거나 자신의 직업군이 착용할 수 없는 장비입니다.')
        embed.add_field(name='> 선택 장비', value=getItemInfo(new_equip))
        embed.add_field(name='> 직업', value=getJobName(adv['job']))
        embed.add_field(name='> 레벨', value=adv['level'])
        await ctx.channel.send(embed=embed)
        return

    equipment = tool.getEquipment(ctx.message.author.id)
    _type = getItemType(inv[index])
    old_equip = equipment.get(_type)

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
                                  description=f"'{new_equip['name']}' 을(를) 성공적으로 장착했습니다.")
            await ctx.channel.send(embed=embed)
        elif str(reaction) == '❌':
            await msg.delete()
            embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 장비 착용",
                                  description=f"장비 착용을 취소했습니다. 더 고민해보고 다시 시도해주세요.")
            await ctx.channel.send(embed=embed)
    except Exception as e:
        print(e)

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

    prob = getReinforceProb(target['reinforce']['value'] + 1)
    cost = getReinforceCost(target['reinforce']['value'] + 1, getItemType(target))

    await msg.delete()
    embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 장비 강화',
                          description='강화를 시도하려면 O, 취소하려면 X 이모지를 추가해주세요.')
    embed.add_field(name='> 선택한 장비', value=f"+{target['reinforce']['value']} {target['name']}")
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
            await doReinforce(bot, ctx, target)
        elif str(reaction) == '❌':
            await msg.delete()
            embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 장비 강화',
                                  description='강화가 취소되었습니다. 다시 한번 생각해보고 시도해주세요.')
            await ctx.channel.send(embed=embed)
    except Exception as e:
        print(e)

async def doReinforce(bot, ctx, target):
    prob = getReinforceProb(target['reinforce']['value'] + 1)
    cost = getReinforceCost(target['reinforce']['value'] + 1, getItemType(target))
    gold = tool.getGold(ctx.message.author.id)
    if gold < cost:
        embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 장비 강화',
                              description='강화에 필요한 골드가 부족합니다.')
        embed.add_field(name='> 장비', value=f"+{target['reinforce']['value']} {target['name']}")
        embed.add_field(name='> 보유 골드', value=f"{format(gold, ',')}골드")
        embed.add_field(name='> 강화 비용', value=f"{format(cost, ',')}골드")
        await ctx.channel.send(embed=embed)
        return

    tool.gainGold(ctx.message.author.id, -cost)

    import random
    seed = random.randint(1, 100)
    if seed <= prob:
        target['reinforce']['value'] += 1
        target['reinforce'].update(getReinforceStat(target))
        tool.setEquipment(ctx.message.author.id, target)

    embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 장비 강화')
    embed.add_field(name='> 장비', value=f"+{target['reinforce']['value']} {target['name']}", inline=False)
    if seed <= prob:
        embed.add_field(name='> 결과', value='성공')
    else:
        embed.add_field(name='> 결과', value='실패')
    embed.add_field(name='> 보유 골드', value=f"{format(gold - cost, ',')}골드")
    embed.add_field(name='> 강화 비용', value=f"{format(cost, ',')}골드")
    embed.set_footer(text=f"⚔️이모지를 추가하면 다시 강화를 시도합니다. (성공 확률 : {getReinforceProb(target['reinforce']['value'] + 1)}%)")
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('⚔️')

    try:
        def check(_reaction, _user):
            return str(_reaction) == '⚔️' and _user == ctx.author and _reaction.message.id == msg.id
        reaction, user = await bot.wait_for('reaction_add', check=check)
        await msg.delete()
        await doReinforce(bot, ctx, target)
    except: pass

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
        _type = getItemType(item)
        if _type == 'weapon':     return weapon_stat[item['reinforce']['value']]
        if _type == 'accessory':  return accessory_stat[item['reinforce']['value']]
        if _type == 'additional': return additional_stat[item['reinforce']['value']]
        else: return None
    except:
        return None