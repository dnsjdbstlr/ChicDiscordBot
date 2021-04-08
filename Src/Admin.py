import discord
from Src import Util
from Database import Connection

ownerId = 247361856904232960

async def 상태(bot, ctx, *state):
    if ctx.message.author.id == ownerId:
        state = Util.mergeString(*state)
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(state))
        await ctx.message.delete()
        await ctx.channel.send("> '" + state + " 하는 중' 으로 상태를 바꿨습니다.")

async def 연결(bot, ctx):
    if ctx.message.author.id == ownerId:
        await ctx.message.delete()
        await ctx.channel.send('> 시크봇은 ' + str(len(bot.guilds)) + '개의 서버에 연결되어있어요!')

async def 통계(ctx):
    commandList = ['!등급', '!캐릭터', '!장비', '!세트', '!시세', '!획득에픽', '!기린랭킹', '!강화랭킹', '!주식', '!주식매수',
                   '!주식매도', '!주식랭킹', '!출석', '!강화설정', '!강화정보', '!강화', '!공개강화', '!청소']
    if ctx.message.author.id == ownerId:
        await ctx.message.delete()
        conn, cur = Connection.getConnection()
        sql = 'SELECT command FROM log WHERE time > CURDATE()'
        cur.execute(sql)
        rs = cur.fetchall()

        statistics = [i['command'].split()[0] for i in rs]
        embed = discord.Embed(title='오늘 명령어 사용 횟수 통계')
        for k in commandList:
            embed.add_field(name='> ' + k, value=str(statistics.count(k)) + '회')
        await ctx.channel.send(embed=embed)

async def 출석확인(ctx):
    if ctx.message.author.id == ownerId:
        await ctx.message.delete()
        try:
            conn, cur = Connection.getConnection()
            sql = f'SELECT * FROM dailyCheck WHERE date=CURDATE()'
            cur.execute(sql)
            rs = cur.fetchall()
        except: return
        await ctx.channel.send(f'> 현재까지 {len(rs)}명이 출석했습니다.')