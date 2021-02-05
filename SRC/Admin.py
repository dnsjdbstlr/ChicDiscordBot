import discord
import json
from SRC import Util
ownerId = 247361856904232960

class userCommandStatistics:
    def __init__(self):
        self.data = {
            '!도움말'   : 0,
            '!등급'     : 0,
            '!캐릭터'   : 0,
            '!장비'     : 0,
            '!세트'     : 0,
            '!시세'     : 0,
            '!획득에픽' : 0,
            '!기린랭킹' : 0,
            '!주식'     : 0,
            '!주식매수' : 0,
            '!주식매도' : 0,
            '!출석'     : 0,
            '!청소'     : 0
        }

        try:
            with open('Data/cmdStatistics.json', 'r') as f:
                temp = json.load(f)
                for k in temp.keys():
                    self.data.update( {k : temp[k]} )
                print('[알림][명령어 통계를 불러왔습니다.]')
        except:
            print('[알림][명령어 통계 데이터가 없습니다.]')

    def update(self):
        # 파일로 저장
        with open('Data/cmdStatistics.json', 'w') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
USER_COMMAND_DATA = userCommandStatistics()

def saveCmdStatistics(msg):
    cmd = msg.content.split(' ')[0]
    if cmd in USER_COMMAND_DATA.data.keys():
        USER_COMMAND_DATA.data[cmd] += 1
        USER_COMMAND_DATA.update()

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
    if ctx.message.author.id == ownerId:
        await ctx.message.delete()
        embed = discord.Embed(title='유저들이 사용한 각 명령어의 사용 횟수를 알려드릴게요.')
        for k in USER_COMMAND_DATA.data.keys():
            embed.add_field(name='> ' + k, value=str(USER_COMMAND_DATA.data[k]) + '번')
        await ctx.channel.send(embed=embed)

async def 출석확인(ctx):
    if ctx.message.author.id == ownerId:
        await ctx.message.delete()
        from SRC import Stock

        count = 0
        for key in Stock.STOCK_DATA.data.keys():
            stock = Stock.STOCK_DATA.data[key]
            if stock['daily'] == Util.getToday2():
                count += 1

        await ctx.channel.send('> ' + Util.getToday2() + ' : ' + str(count) + '명이 출석체크를 했어요!')
