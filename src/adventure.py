import discord
from database import connection

info = {
    100: {
        '타입': '대검',
        '공격력': 10,
        '스탯': 5,
        '체력': 10,
        '마력': 5
    },
    101: {
        '타입': '자동권총',
        '공격력': 5,
        '스탯': 10,
        '체력': 10,
        '마력': 10
    },
    102: {
        '타입': '스탭',
        '공격력': 10,
        '스탯': 5,
        '체력': 10,
        '마력': 30
    },

    200: {
        '타입': '대검',
        '공격력': 30,
        '스탯': 10,
        '체력': 15,
        '마력': 5
    },
    201: {
        '타입': '자동권총',
        '공격력': 15,
        '스탯': 15,
        '체력': 10,
        '마력': 10
    },
    202: {
        '타입': '스탭',
        '공격력': 30,
        '스탯': 5,
        '체력': 15,
        '마력': 50
    },

    300: {
        '타입': '대검',
        '공격력': 80,
        '스탯': 30,
        '체력': 50,
        '마력': 30
    },
    301: {
        '타입': '자동권총',
        '공격력': 50,
        '스탯': 50,
        '체력': 50,
        '마력': 50
    },
    302: {
        '타입': '스탭',
        '공격력': 100,
        '스탯': 10,
        '체력': 20,
        '마력': 100
    },

    400: {
        '타입': '대검',
        '공격력': 200,
        '스탯': 80,
        '체력': 100,
        '마력': 50,
    },
    401: {
        '타입': '자동권총',
        '공격력': 120,
        '스탯': 120,
        '체력': 80,
        '마력': 80
    },
    402: {
        '타입': '스탭',
        '공격력': 250,
        '스탯': 10,
        '체력': 20,
        '마력': 100
    },
}

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
        sql = f'INSERT INTO adventure (did, job, level, exp) values ({ctx.message.author.id}, 0, 1, 0)'
        cur.execute(sql)
        conn.commit()

        sql = f'SELECT * FROM adventure WHERE did={ctx.message.author.id}'
        cur.execute(sql)
        rs = cur.fetchone()

    embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 모험 정보를 알려드릴게요.')
    embed.add_field(name='> 직업',     value=getJobInfo(rs['job']))
    embed.add_field(name='> 레벨',     value=getLevelInfo(rs['level']))
    embed.add_field(name='> 경험치',   value=getExpInfo(rs['level'], rs['exp']))
    embed.add_field(name='> 장착장비', value=rs['equipment'])
    embed.add_field(name='> 인벤토리', value=rs['inventory'])
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

async def 모험뽑기(bot, ctx):
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
    embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 모험 뽑기',
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

        sql = f'UPDATE stock SET gold=%s WHERE did=%s'
        cur.execute(sql, (rs['gold'] - (100000 * count), ctx.message.author.id))
        conn.commit()
    except Exception as e:
        await ctx.channel.send(f'> 뽑기에 실패했습니다.\r\n{e}')
        return

    ###

    reward = getGachaReward(count)
    desc = getRewardDesc(reward)
    embed = discord.Embed(title=f'{ctx.message.author.display_name}님의 모험 뽑기 결과', description=f"`{desc}`")
    for index, i in enumerate(reward['reward']):
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
    result = {
        'reward' : [],
        'count'  : [0, 0, 0, 0]}
    unique    = [100, 101, 102]
    legendary = [200, 201, 202]
    epic      = [300, 301, 302]
    mythic    = [400, 401, 402]

    for i in range(count):
        seed = random.randint(1, 100)
        if 1 <= seed <= 70:
            result['reward'].append(random.choice(unique))
            result['count'][0] += 1
        elif 70 < seed <= 90:
            result['reward'].append(random.choice(legendary))
            result['count'][1] += 1
        elif 90 < seed <= 99:
            result['reward'].append(random.choice(epic))
            result['count'][2] += 1
        else:
            result['reward'].append(random.choice(mythic))
            result['count'][3] += 1
    return result

def getRewardDesc(reward):
    desc = ''
    if reward['count'][0] > 0:
        desc += f"유니크 : {reward['count'][0]}개"
    if reward['count'][1] > 0:
        if desc != '': desc += ' | '
        desc += f"레전더리 : {reward['count'][1]}개"
    if reward['count'][2] > 0:
        if desc != '': desc += ' | '
        desc += f"에픽 : {reward['count'][2]}개"
    if reward['count'][3] > 0:
        if desc != '': desc += ' | '
        desc += f"신화 : {reward['count'][3]}개"
    return desc

def getItemInfo(item):
    if info.get(item) is None:
        return 'ERR'

    if item // 100 == 1:
        desc = '유니크 '
    elif item // 100 == 2:
        desc = '레전더리 '
    elif item // 100 == 3:
        desc = '에픽 '
    elif item // 100 == 4:
        desc = '신화 '
    else:
        return 'ERR'

    for i in info.get(item):
        if i == '타입':
            desc += info.get(item)[i] + '\r\n'
        else:
            desc += f"{i} : {info.get(item)[i]}\r\n"
    return desc