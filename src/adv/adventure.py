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
        inventory = { 'weapon' : None, 'accessory' : None, 'additional' : None }
        sql = 'INSERT INTO adventure values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
        cur.execute(sql, (ctx.message.author.id, 0, 1, 0, 5, 0, 0, 50, 50, json.dumps(inventory), json.dumps(inventory)))
        conn.commit()

        sql = f'SELECT * FROM adventure WHERE did={ctx.message.author.id}'
        cur.execute(sql)
        rs = cur.fetchone()

    embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 모험 정보를 알려드릴게요.')
    embed.add_field(name='> 직업',     value=getJobInfo(rs['job']))
    embed.add_field(name='> 레벨',     value=getLevelInfo(rs['level']))
    embed.add_field(name='> 경험치',   value=getExpInfo(rs['level'], rs['exp']))
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

def getItemInfo(item):
    try:
        desc = f"+{item['info']['reinforce']} {item['info']['name']} ({getWeaponType(item['info']['id'])})\r\n"
        for key in item['option']:
            desc += f"{key} : {item['option'][key]}\r\n"
        return desc
    except:
        return '없음'

# desc = f'{rarity} {_type}\r\n'
# for key in WEAPON.get(itemId):
#     desc += f"{key} : {WEAPON.get(itemId)[key]}\r\n"
# return desc

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

async def 무기가챠(bot, ctx):
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
        await ctx.channel.send(str(e))
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

        if inv is not None and len(inv['data']) + count > 45:
            await ctx.channel.send(f'> 인벤토리 공간이 부족합니다.')
            return

        sql = f'UPDATE stock SET gold=%s WHERE did=%s'
        cur.execute(sql, (rs['gold'] - (100000 * count), ctx.message.author.id))
        conn.commit()
    except Exception as e:
        await ctx.channel.send(f'> 뽑기에 실패했습니다.\r\n{e}')
        return

    ###

    reward, summary = getGachaReward(count)
    saveGachaReward(reward, ctx.message.author.id)
    desc = getRewardSummaryDesc(summary)

    embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 모험 뽑기 결과', description=f"`{desc}`")
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

def getGachaReward(count):
    import random
    reward  = []
    summary = [0, 0, 0, 0]

    unique    = [100, 101, 102]
    legendary = [200, 201, 202]
    epic      = [300, 301, 302]
    mythic    = [400, 401, 402]

    for i in range(count):
        seed = random.randint(1, 100)
        if 1 <= seed <= 70:
            reward.append(random.choice(unique))
            summary[0] += 1
        elif 70 < seed <= 90:
            reward.append(random.choice(legendary))
            summary[1] += 1
        elif 90 < seed <= 99:
            reward.append(random.choice(epic))
            summary[2] += 1
        else:
            reward.append(random.choice(mythic))
            summary[3] += 1
    return reward, summary

def saveGachaReward(reward, did):
    try:
        conn, cur = connection.getConnection()
        sql = f'SELECT * FROM adventure WHERE did={did}'
        cur.execute(sql)
        rs = cur.fetchone()
        rs = rs['inventory']
    except: return
    if rs is None:
        rs = {'data' : []}
    else:
        rs = json.loads(rs)

    for i in reward:
        rs['data'].append(createItem(i))

    try:
        sql = f'UPDATE adventure SET inventory=%s WHERE did={did}'
        cur.execute(sql, json.dumps(rs, ensure_ascii=False))
        conn.commit()
    except Exception as e:
        print(f'> 업데이트 오류\r\n> {e}')
        return

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
    if itemId // 100 == 1:
        rarity = '유니크 '
    elif itemId // 100 == 2:
        rarity = '레전더리 '
    elif itemId // 100 == 3:
        rarity = '에픽 '
    elif itemId // 100 == 4:
        rarity = '신화 '
    else:
        rarity = 'Err'

    if itemId % 10 == 0:
        _type = '대검'
    elif itemId % 10 == 1:
        _type = '자동권총'
    elif itemId % 10 == 2:
        _type = '스탭'
    else:
        _type = 'Err'

    info = {
        'id' : itemId,
        'type' : _type,
        'rarity' : rarity
    }
    option = WEAPON[itemId]
    return {'info' : info, 'option' : option, 'reinforce' : 0}

async def 인벤토리(bot, ctx):
    try:
        conn, cur = connection.getConnection()
        sql = f'SELECT * FROM adventure WHERE did={ctx.message.author.id}'
        cur.execute(sql)
        rs = cur.fetchone()
        rs = rs['inventory']

        try:
            rs = json.loads(rs)
            inv = rs['data']
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
    await setEquipItem(ctx, inv, selection)

async def getInventorySelection(bot, ctx, inv, page,
                                title=None, description=None, msg=None):
    _inv = inv[page * 9 : page * 9 + 9]

    if title is not None and description is not None:
        embed = discord.Embed(title=title, description=description)
    else:
        embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 모험 인벤토리를 보여드릴게요.",
                              description=f"장착하고 싶은 아이템의 번호와 동일한 이모지를 추가해주세요.")
    for index, item in enumerate(_inv):
        embed.add_field(name=f"> {index + 1}", value=getInvItemInfo(item))
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

async def setEquipItem(ctx, inv, index):
    equip = inv[index]
    del inv[index]
    try:
        conn, cur = connection.getConnection()
        sql = f'UPDATE adventure SET inventory=%s, equipment=%s WHERE did={ctx.message.author.id}'
        cur.execute(sql, (json.dumps({'data' : inv}, ensure_ascii=False), json.dumps(equip, ensure_ascii=False)))
        conn.commit()

    except Exception as e:
        await ctx.channel.send(f'> 장비를 장착하는데 오류가 발생했습니다.\r\n> {e}')
        return

    embed = discord.Embed(title=f"{ctx.message.author.display_name}님의 장비 착용",
                          description='장착되어있는 장비는 사라져요. 선택한 장비를 착용할까요?')
    embed.add_field(name='> 장착 장비', value=getInvItemInfo(equip))
    await ctx.channel.send(embed=embed)
