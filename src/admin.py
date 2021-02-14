import json
import discord
from src import util
from datetime import datetime
from database import connection
ownerId = 247361856904232960

cmds = ['!등급', '!캐릭터', '!장비', '!세트', '!시세',
        '!획득에픽', '!기린랭킹',
        '!주식', '!주식매수', '!주식매도', '!주식랭킹', '!출석',
        '!청소']

def log(msg):
    cmd = msg.content.split(' ')[0]
    if cmd in cmds:
        try:
            conn, cur = connection.getConnection()
            sql = 'INSERT INTO log (did, gid, command, time) values (%s, %s, %s, %s)'
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cur.execute(sql, (msg.author.id, msg.guild.id, msg.content, date))
            conn.commit()
        finally:
            conn.close()

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
        wait = await ctx.channel.send('> 통계 데이터를 불러오고있어요...')

        try:
            conn, cur = connection.getConnection()
            sql = 'SELECT command FROM log'
            cur.execute(sql)
            rs = cur.fetchall()
            
            statistics = [i['command'].split(' ')[0] for i in rs]
            embed = discord.Embed(title='유저들이 사용한 각 명령어의 사용 횟수를 알려드릴게요.')
            for k in cmds:
                embed.add_field(name='> ' + k, value=str(statistics.count(k)) + '회')
            await wait.delete()
            await ctx.channel.send(embed=embed)
        finally:
            conn.close()
