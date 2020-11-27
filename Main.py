import discord
from discord.ext import commands
import os
import re
import requests

# 기본설정
app = commands.Bot(command_prefix='!')
token = os.environ['token']

@app.event
async def on_ready():
    await app.change_presence(status=discord.Status.online, activity=discord.Game('공부'))
    print('로그인 완료!')

@app.event
async def on_disconnect():
    await app.change_presence(status=discord.Status.offline)

@app.event
async def on_message(msg):
    await app.process_commands(msg)

    if msg.author.bot:
        return None

@app.command()
async def 도움말(ctx):
    await ctx.channel.purge(limit=1)
    embed = discord.Embed(title='시크봇의 도움말을 알려드릴게요!')
    embed.add_field(name='!등급', value='오늘의 장비 등급을 알려드릴게요.', inline=False)
    embed.add_field(name='!기린력 <서버> <닉네임>', value='당신의 기린력을 알려드릴게요.', inline=False)
    await ctx.channel.send(embed=embed)

@app.command()
async def 기린력(ctx, server='None', name='None'):
    if (server == 'None' or name == 'None'):
        await ctx.channel.purge(limit=1)
        await ctx.channel.send('!기린력 <서버> <닉네임> 의 형태로 적어야해!')
        return
    else:
        await ctx.channel.purge(limit=1)
        await ctx.channel.send(name + '님의 기린력을 측정하고 있어요!')

    # URL만들기
    url = 'http://duntoki.xyz/giraffe?serverNm=' + server + '&charNm=' + name
    response = requests.get(url=url)
    if response.status_code == 200:
        # 패턴 정의
        pat1 = [None, None, None, None]
        pat1[0] = re.compile('(?P<date>\d\d\d\d-\d\d-\d\d) 대비-(?P<delta>\d.\d\d점 하락)')
        pat1[1] = re.compile('(?P<date>\d\d\d\d-\d\d-\d\d) 대비-(?P<delta>\d\d.\d\d점 하락)')
        pat1[2] = re.compile('(?P<date>\d\d\d\d-\d\d-\d\d) 대비(?P<delta>\d.\d\d점 상승)')
        pat1[3] = re.compile('(?P<date>\d\d\d\d-\d\d-\d\d) 대비(?P<delta>\d\d.\d\d점 상승)')

        pat2 = [None, None, None]
        pat2[0] = re.compile('<td>(?P<grade>\d\.\d점)</td>')
        pat2[1] = re.compile('<td>(?P<grade>\d\.\d\d점)</td>')
        pat2[2] = re.compile('<td>(?P<grade>\d\d\.\d\d점)</td>')

        # 결과
        result0 = None
        for i in range(4):
            result0 = pat1[i].search(response.text)
            if result0 != None: break

        result1 = None
        for i in range(3):
            result1 = pat2[i].search(response.text)
            if result1 != None: break

        # 출력
        await ctx.channel.purge(limit=1)
        try:
            if result0 is not None:
                embed = discord.Embed(title='기린력 측정 결과가 나왔어요!',
                                      description=name + '님의 기린력은 ' + result0.group('date') + '때 보다 ' + result0.group('delta') + '한 ' + result1.group('grade') + '입니다!')
                await ctx.channel.send(embed=embed)
            else:
                await ctx.channel.send(name + '님의 기린력은 ' + result1.group('grade') + '입니다!')
        except:
            await ctx.channel.send('기린력을 읽어오지 못했어...')
    else:
        await ctx.channel.purge(limit=1)
        await ctx.channel.send('뭔가 오류가 났어...')

@app.command()
async def 등급(ctx):
    url = 'http://dnfnow.xyz/class'
    response = requests.get(url=url)

    # 계산
    pat = []
    pat.append(re.compile('<span class="badge badge-warning">'))
    pat.append(re.compile('</span>'))

    temp0 = pat[0].search(response.text)
    start0, end0 = temp0.start(), temp0.end()

    temp1 = pat[1].search(response.text[end0:])
    start1, end1 = temp1.start(), temp1.end()

    result = response.text[end0 + 1 : end0 + start1 - 1].replace(' ', '').replace('\n', '')
    
    # 출력
    await ctx.channel.purge(limit=1)
    embed = discord.Embed(title='아이템 등급을 알려드릴게요!', description='오늘의 등급은 천공의 유산 - 소검을 기준으로 ' + result + '이예요!')
    await ctx.channel.send(embed=embed)

app.remove_command('help')
app.run(token)