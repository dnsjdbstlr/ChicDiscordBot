import json
import discord
from src.adv import item
from database import connection

async def 모험(ctx):
    try:
        conn, cur = connection.getConnection()
        sql = f'SELECT * FROM adventure WHERE did={ctx.message.author.id}'
        cur.execute(sql)
        rs = cur.fetchone()
    except Exception as e:
        await ctx.channel.send(f'> 모험 정보를 불러오지 못했어요.\r\n> {e}')
        return

    if rs is None:
        inventory = { 'inventory' : [] }
        equipment = { 'weapon' : [], 'accessory' : [], 'additional' : [] }
        sql = 'INSERT INTO adventure values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cur.execute(sql, (ctx.message.author.id, 0, 1, 0, 5, 0, 0, 50, 50, json.dumps(inventory), json.dumps(equipment)))
        conn.commit()

        sql = f'SELECT * FROM adventure WHERE did={ctx.message.author.id}'
        cur.execute(sql)
        rs = cur.fetchone()

    embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 모험 정보를 알려드릴게요.')
    embed.add_field(name='> 직업',     value=getJobInfo(rs['job']))
    embed.add_field(name='> 레벨',     value=getLevelInfo(rs['level']))
    embed.add_field(name='> 경험치',   value=getExpInfo(rs['level'], rs['exp']))
    embed.add_field(name='> 능력치',   value=getStatInfo(rs['equipment'], rs['ap'], rs['def'], rs['stat'], rs['maxhp'], rs['maxmp']), inline=False)
    embed.add_field(name='> 장착장비', value=getItemInfo( json.loads(rs['equipment']) ))
    await ctx.message.delete()
    await ctx.channel.send(embed=embed)

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

def getStatInfo(equipment, ap, _def, stat, maxhp, maxmp):
    equipment = json.loads(equipment)
    cri, dmgInc, criDmgInc = 10, 0, 0

    for i in equipment:
        try:
            temp = equipment[i]['option'].get('치명타 확률')
            if temp is not None:
                cri += temp
        except: pass

        try:
            temp = equipment[i]['option'].get('데미지 증가')
            if temp is not None:
                dmgInc += temp
        except: pass

        try:
            temp = equipment[i]['option'].get('치명타 데미지 증가')
            if temp is not None:
                criDmgInc += temp
        except: pass

    desc = f'공격력 : {ap} | 방어력 : {_def} | 스탯 : {stat} | 체력 : {maxhp} | 마력 : {maxmp}\r\n'
    desc += f'치명타 확률 : {cri}% | 데미지 증가 : {dmgInc}% | 치명타 데미지 증가 : {criDmgInc}%'
    return desc

def getItemInfo(item):
    try:
        if item['info']['reinforce'] > 0:
            desc = f"+{item['info']['reinforce']} "
        else:
            desc = ''
        desc += f"{item['info']['name']}\r\n"
        desc += f"타입 : {item['info']['rarity']} {getWeaponType(item['info']['id'])}\r\n"
        for key in item['option']:
            desc += f"{key} : {item['option'][key]}"
            if key in ['추가데미지']:
                desc += '%\r\n'
            else:
                desc += '\r\n'
        return desc
    except:
        return '없음'

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

async def 장비뽑기(bot, ctx):
    try:
        conn, cur = connection.getConnection()
        sql = f'SELECT * FROM stock WHERE did={ctx.message.author.id}'
        cur.execute(sql)
        rs = cur.fetchone()
    except Exception as e:
        await ctx.message.delete()
        await ctx.channel.send(f'> 주식 정보를 불러오지 못했어요.\r\n> {e}')
        return
    if rs is None:
        await ctx.message.delete()
        await ctx.channel.send('> !주식 명령어를 사용한 뒤에 다시 시도해주세요.')
        return
    embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 무기 가챠',
                          description='과도한 뽑기는 정신건강에 영향을 줄 수도 있어요.')
    embed.add_field(name='> 보유 금액', value=f"{format(rs['gold'], ',')}골드")
    embed.add_field(name='> 3회 뽑기',  value=f"300,000골드")
    embed.add_field(name='> 9회 뽑기', value=f"900,000골드")

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

async def gacha(bot, ctx, count):
    try:
        conn, cur = connection.getConnection()
        sql = f'SELECT * FROM stock WHERE did={ctx.message.author.id}'
        cur.execute(sql)
        rs = cur.fetchone()

        if rs['gold'] - (100000 * count) < 0:
            await ctx.channel.send(f'> 뽑기에 필요한 골드가 부족합니다.')
            return

        sql = f'SELECT * FROM adventure WHERE did={ctx.message.author.id}'
        cur.execute(sql)
        _rs = cur.fetchone()

        try:
            inv = json.loads(_rs['inventory'])
        except:
            inv = None

        if inv is not None and len(inv['inventory']) + count > 45:
            await ctx.channel.send(f'> 인벤토리 공간이 부족합니다.')
            return
    except Exception as e:
        await ctx.channel.send(f'> 뽑기에 실패했습니다.\r\n{e}')
        return

    ###

    reward = doGacha(ctx, count)
    embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 모험 뽑기 결과')
    for index, i in enumerate(reward):
        embed.add_field(name=f"> {index + 1}", value=getItemInfo(i))
    embed.set_footer(text=f'🔁 이모지를 추가하면 {count}번 뽑기를 진행합니다.')
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('🔁')

    while True:
        try:
            def check(reaction, user):
                return str(reaction) == '🔁' and user == ctx.author and reaction.message.id == msg.id
            reaction, user = await bot.wait_for('reaction_add', check=check)
            await msg.delete()
            await gacha(bot, ctx, count)
        except: pass

def doGacha(ctx, count):
    reward = []

    import random
    for i in range(count):
        part = random.choice(['weapon'])
        if part == 'weapon':
            legendary = [10000, 10100, 10200, 10300, 10400]
            epic      = []
            mythic    = []

            seed = random.randint(1, 100)
            if 1 <= seed <= 100:
                itemId = random.choice(legendary)
                reward.append(createItem(itemId))

    # 인벤토리 저장
    try:
        conn, cur = connection.getConnection()
        sql = f'SELECT * FROM adventure WHERE did={ctx.message.author.id}'
        cur.execute(sql)
        rs = cur.fetchone()
        rs = rs['inventory']

        if rs is None:
            rs = {'inventory': []}
        else:
            rs = json.loads(rs)
        for i in reward: rs['inventory'].append(i) 

        sql = f'UPDATE adventure SET inventory=%s WHERE did={ctx.message.author.id}'
        cur.execute(sql, json.dumps(rs, ensure_ascii=False))
        conn.commit()
    except Exception as e:
        print(e)
        return None
    return reward

def getRewardSummaryDesc(summary):
    desc = ''
    if summary[0] > 0:
        desc += f"유니크 : {summary[0]}개"
    if summary[1] > 0:
        if desc != '': desc += ' | '
        desc += f"레전더리 : {summary[1]}개"
    if summary[2] > 0:
        if desc != '': desc += ' | '
        desc += f"에픽 : {summary[2]}개"
    if summary[3] > 0:
        if desc != '': desc += ' | '
        desc += f"신화 : {summary[3]}개"
    return desc

def createItem(itemId):
    if itemId // 10000 == 1:
        return item.WEAPON.get(str(itemId))
    else:
        return None

async def 인벤토리(bot, ctx):
    try:
        conn, cur = connection.getConnection()
        sql = f'SELECT * FROM adventure WHERE did={ctx.message.author.id}'
        cur.execute(sql)
        rs = cur.fetchone()
        rs = rs['inventory']

        try:
            rs = json.loads(rs)
            inv = rs['inventory']
        except:
            embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 모험 인벤토리를 보여드릴게요.",
                                  description=f"인벤토리에 아이템이 없어요! `!모험뽑기` 를 통해서 아이템을 획득해보세요.")
            await ctx.message.delete()
            await ctx.channel.send(embed=embed)
            return
    except Exception as e:
        await ctx.channel.send(f'> 모험 데이터를 불러오는데 실패했습니다.\r\n> {e}')
        return

    if not inv:
        embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 모험 인벤토리를 보여드릴게요.",
                              description=f"인벤토리에 아이템이 없어요! `!모험뽑기` 를 통해서 아이템을 획득해보세요.")
        await ctx.message.delete()
        await ctx.channel.send(embed=embed)
        return

    await ctx.message.delete()
    selection = await getInventorySelection(bot, ctx, inv, 0)
    await setEquipItem(bot, ctx, inv, selection)

async def getInventorySelection(bot, ctx, inv, page,
                                title=None, description=None, msg=None):
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

async def setEquipItem(bot, ctx, inv, index):

    # del inv[index]
    # try:
    #     conn, cur = connection.getConnection()
    #     sql = f'UPDATE adventure SET inventory=%s, equipment=%s WHERE did={ctx.message.author.id}'
    #     cur.execute(sql, (json.dumps({'inventory' : inv}, ensure_ascii=False), json.dumps(equip, ensure_ascii=False)))
    #     conn.commit()
    # except Exception as e:
    #     await ctx.channel.send(f'> 장비를 장착하는데 오류가 발생했습니다.\r\n> {e}')
    #     return

    try:
        conn, cur = connection.getConnection()
        sql = f'SELECT * FROM adventure WHERE did={ctx.message.author.id}'
        cur.execute(sql)
        rs = cur.fetchone()
    except: return

    equipment = json.loads(rs['equipment'])

    new_equip = inv[index]
    if new_equip['info']['id'] // 10000 == 1:
        _type = 'weapon'
    elif new_equip['info']['id'] // 10000 == 2:
        _type = 'accessory'
    elif new_equip['info']['id'] // 10000 == 3:
        _type = 'additional'
    else:
        _type = 'err'
    old_equip = equipment[_type]

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
            await msg.delete()
            await ctx.channel.send(f"대충 성공적으로 장착했다는 메세지")
        elif str(reaction) == '❌':
            await msg.delete()
            await ctx.channel.send('> 장착이 취소되었습니다.')
    except: pass
