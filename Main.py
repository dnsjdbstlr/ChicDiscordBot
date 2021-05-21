import discord
import os
from discord.ext import commands, tasks
from Src import Account, Admin, Etc, Measure, Reinfoce, Search, Trading, Util

### 선언 ###
bot = commands.Bot(command_prefix='!')
bot_token = os.environ['bot_token']

### 이벤트 ###
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('!도움말'))
    print('[알림][시크봇이 성공적으로 구동됬습니다.]')

@bot.event
async def on_message(msg):
    if msg.author.bot: return None
    chicBotChannel = Util.getChicBotChannel(msg.guild)
    if not chicBotChannel or msg.channel in chicBotChannel:
        await bot.process_commands(msg)

### 검색 ###
@bot.command()
async def 등급(ctx):
    await Search.등급(ctx)

@bot.command()
async def 캐릭터(ctx, *input):
    await Search.캐릭터(bot, ctx, *input)

@bot.command()
async def 장비(ctx, *input):
    await Search.장비(bot, ctx, *input)

@bot.command()
async def 세트(ctx, *input):
    await Search.세트(bot, ctx, *input)

@bot.command()
async def 시세(ctx, *input):
    await Search.시세(bot, ctx, *input)

@bot.command()
async def 에픽(ctx, *input):
    await Search.에픽(bot, ctx, *input)

@bot.command()
async def 에픽랭킹(ctx):
    await Search.에픽랭킹(bot, ctx)

### 측정 ###
@bot.command()
async def 버프력(ctx, *input):
    await Measure.버프력(bot, ctx, *input)

### 계정 ###
@bot.command()
async def 출석(ctx):
    await Account.출석(ctx)

@bot.command()
async def 출첵(ctx):
    await Account.출석(ctx)

@bot.command()
async def 출석체크(ctx):
    await Account.출석(ctx)

### 거래 ###
@tasks.loop(minutes=1)
async def updateMarketPrice():
    Trading.updateMarketPrices()
updateMarketPrice.start()

@bot.command()
async def 선물거래(ctx):
    await Trading.선물거래(ctx)

@bot.command()
async def 주문(ctx, *input):
    await Trading.주문(bot, ctx, *input)

@bot.command()
async def 포지션(ctx):
    await Trading.포지션(bot, ctx)

@bot.command()
async def 거래내역(ctx):
    await Trading.거래내역(bot, ctx)

@bot.command()
async def 파산(ctx):
    await Trading.파산(bot, ctx)

@bot.command()
async def 골드랭킹(ctx):
    await Trading.골드랭킹(bot, ctx)

### 강화 ###
@bot.command()
async def 강화설정(ctx, *input):
    await Reinfoce.강화설정(bot, ctx, *input)

@bot.command()
async def 강화정보(ctx):
    await Reinfoce.강화정보(ctx)

@bot.command()
async def 강화(ctx):
    await Reinfoce.강화(bot, ctx)

@bot.command()
async def 공개강화(ctx):
    await Reinfoce.공개강화(bot, ctx)

@bot.command()
async def 강화랭킹(ctx):
    await Reinfoce.강화랭킹(bot, ctx)

### 기타 ###
@bot.command()
async def 도움말(ctx):
    await Etc.도움말(bot, ctx)

@bot.command()
async def 명령어(ctx):
    await Etc.도움말(bot, ctx)

@bot.command()
async def 청소(ctx):
    await Etc.청소(bot, ctx)

### 관리자 ###
@bot.command()
async def 연결(ctx):
    await Admin.연결(bot, ctx)

@bot.command()
async def 상태(ctx, *input):
    await Admin.상태(bot, ctx, *input)

bot.remove_command('help')
bot.run(bot_token)
