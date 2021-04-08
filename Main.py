import os
import discord
from discord.ext import commands
from Database import Tool
from Src import Account, Admin, Etc, Reinfoce, Search, Stock, Util

# # # 설 정 # # #
bot = commands.Bot(command_prefix='!')
bot_token = os.environ['bot_token']

# # # 이 벤 트 # # #
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('!도움말'))
    print('[알림][시크봇이 성공적으로 구동됬습니다.]')

@bot.event
async def on_message(msg):
    if msg.author.bot: return None
    Tool.log(msg)
    chicBotChannel = Util.getChicBotChannel(msg.guild)
    if not chicBotChannel or msg.channel in chicBotChannel:
        await bot.process_commands(msg)

# # # 검 색 # # #
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
    await Search.시세(ctx, *input)

@bot.command()
async def 획득에픽(ctx, *input):
    await Search.획득에픽(bot, ctx, *input)

@bot.command()
async def 기린랭킹(ctx):
    await Search.기린랭킹(bot, ctx)

# # # 계 정 # # #
@bot.command()
async def 출석(ctx):
    await Account.출석(ctx)

@bot.command()
async def 출첵(ctx):
    await Account.출석(ctx)

@bot.command()
async def 출석체크(ctx):
    await Account.출석(ctx)

# # # 주 식 # # #
@bot.command()
async def 주식(ctx):
    await Stock.주식(ctx)

@bot.command()
async def 매수(ctx, *input):
    await Stock.매수(bot, ctx, *input)

@bot.command()
async def 매도(ctx):
    await Stock.매도(bot, ctx)

@bot.command()
async def 주식랭킹(ctx):
    await Stock.주식랭킹(bot, ctx)

# # # 강 화 # # #
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

# # # 기 타 # # #
@bot.command()
async def 도움말(ctx):
    await Etc.도움말(bot, ctx)

@bot.command()
async def 명령어(ctx):
    await Etc.도움말(bot, ctx)

@bot.command()
async def 청소(ctx):
    await Etc.청소(bot, ctx)

# # # 관 리 자 # # #
@bot.command()
async def 연결(ctx):
    await Admin.연결(bot, ctx)

@bot.command()
async def 상태(ctx, *state):
    await Admin.상태(bot, ctx, *state)

@bot.command()
async def 통계(ctx):
    await Admin.통계(ctx)

@bot.command()
async def 출석확인(ctx):
    await Admin.출석확인(ctx)

bot.remove_command('help')
bot.run(bot_token)
