import discord
import datetime
from src import util
from database import connection

ownerId = 247361856904232960

cmds = ['!등급', '!캐릭터', '!장비', '!세트', '!시세',
        '!획득에픽', '!기린랭킹',
        '!주식', '!주식매수', '!주식매도', '!주식랭킹', '!출석',
        '!강화설정', '!강화정보', '!강화', '!공개강화',
        '!청소']

def log(msg):
    cmd = msg.content.split(' ')[0]
    if cmd in cmds:
        try:
            conn, cur = connection.getConnection()
            sql = 'INSERT INTO log (did, gid, command, time) values (%s, %s, %s, %s)'
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cur.execute(sql, (msg.author.id, msg.guild.id, msg.content, date))
            conn.commit()
        except Exception as e:
            print(e)

async def 상태(bot, ctx, *state):
    if ctx.message.author.id == ownerId:
        state = util.mergeString(*state)
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(state))
        await ctx.message.delete()
        await ctx.channel.send("> '" + state + " 하는 중' 으로 상태를 바꿨습니다.")

async def 연결(bot, ctx):
    if ctx.message.author.id == ownerId:
        await ctx.message.delete()
        await ctx.channel.send('> 시크봇은 ' + str(len(bot.guilds)) + '개의 서버에 연결되어있어요!')

async def 통계(ctx):
    if ctx.message.author.id == ownerId:
        await ctx.message.delete()
        try:
            conn, cur = connection.getConnection()
            sql = 'SELECT command FROM log WHERE date=CURDATE()'
            cur.execute(sql)
            rs = cur.fetchall()

            statistics = [i['command'].split(' ')[0] for i in rs]
            embed = discord.Embed(title='오늘 명령어 사용 횟수 통계')
            for k in cmds:
                embed.add_field(name='> ' + k, value=str(statistics.count(k)) + '회')
            await ctx.channel.send(embed=embed)
        except: return

async def 출석확인(ctx):
    if ctx.message.author.id == ownerId:
        await ctx.message.delete()
        try:
            conn, cur = connection.getConnection()
            sql = f'SELECT * FROM dailyCheck WHERE date=CURDATE()'
            cur.execute(sql)
            rs = cur.fetchall()
        except: return
        await ctx.channel.send(f'> 현재까지 {len(rs)}명이 출석했습니다.')
