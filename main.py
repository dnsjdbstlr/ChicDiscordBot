import discord
from discord.ext import commands
from database import tool
from src import search, stock, reinfoce, admin, etc, util

# # # 설 정 # # #
bot = commands.Bot(command_prefix='!')
token = 'NzgxNzgyNzQ5NDc5Njk4NDQy.X8Cp7A.wJ69VOJUvfEMnv6-F63QG8KNans'
#token = 'NzgyMTc4NTQ4MTg1NTYzMTQ3.X8Iaig.0o0wUqoz8j_iub3SC7A5SFY83U4'

# # # 이 벤 트 # # #
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('!도움말'))
    print('[알림][시크봇이 성공적으로 구동됬습니다.]')

@bot.event
async def on_message(msg):
    if msg.author.bot: return None
    tool.log(msg)
    chicBotChannel = util.getChicBotChannel(msg.guild)
    if not chicBotChannel or msg.channel in chicBotChannel:
        await bot.process_commands(msg)

# # # 검 색 # # #
@bot.command()
async def 등급(ctx):
    await search.등급(ctx)

@bot.command()
async def 캐릭터(ctx, *input):
    await search.캐릭터(bot, ctx, *input)

@bot.command()
async def 장비(ctx, *input):
    await search.장비(bot, ctx, *input)

@bot.command()
async def 세트(ctx, *input):
    await search.세트(bot, ctx, *input)

@bot.command()
async def 시세(ctx, *input):
    await search.시세(ctx, *input)

@bot.command()
async def 획득에픽(ctx, *input):
    await search.획득에픽(bot, ctx, *input)

@bot.command()
async def 기린랭킹(ctx):
    await search.기린랭킹(bot, ctx)

# # # 출 석 # # #
@bot.command()
async def 출석(ctx):
    await stock.출석(ctx)

@bot.command()
async def 출석체크(ctx):
    await stock.출석(ctx)

# # # 주 식 # # #
@bot.command()
async def 주식(ctx):
    await stock.주식(ctx)

@bot.command()
async def 주식매수(ctx, *input):
    await stock.주식매수(bot, ctx, *input)

@bot.command()
async def 주식매도(ctx):
    await stock.주식매도(bot, ctx)

@bot.command()
async def 주식랭킹(ctx):
    await stock.주식랭킹(bot, ctx)

# # # 강 화 # # #
@bot.command()
async def 강화설정(ctx, *input):
    await reinfoce.강화설정(bot, ctx, *input)

@bot.command()
async def 강화정보(ctx):
    await reinfoce.강화정보(ctx)

@bot.command()
async def 강화(ctx):
    await reinfoce.강화(bot, ctx)

@bot.command()
async def 공개강화(ctx):
    await reinfoce.공개강화(bot, ctx)

# # # 기 타 # # #
@bot.command()
async def 도움말(ctx):
    await etc.도움말(bot, ctx)

@bot.command()
async def 명령어(ctx):
    await etc.도움말(bot, ctx)

@bot.command()
async def 청소(ctx):
    await etc.청소(bot, ctx)

# # # 관 리 자 # # #
@bot.command()
async def 연결(ctx):
    await admin.연결(bot, ctx)

@bot.command()
async def 상태(ctx, *state):
    await admin.상태(bot, ctx, *state)

@bot.command()
async def 통계(ctx):
    await admin.통계(ctx)

@bot.command()
async def 출석확인(ctx):
    await admin.출석확인(ctx)

bot.remove_command('help')
bot.run(token)
