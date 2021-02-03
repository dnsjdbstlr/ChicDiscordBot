import discord
from discord.ext import commands
from FrameWork import Classes
from SRC import Search, Ranking, Admin, Etc
bot = commands.Bot(command_prefix='!')

### 기본설정 ###
#token = 'NzgxNzgyNzQ5NDc5Njk4NDQy.X8Cp7A.wJ69VOJUvfEMnv6-F63QG8KNans'
token   = 'NzgyMTc4NTQ4MTg1NTYzMTQ3.X8Iaig.0o0wUqoz8j_iub3SC7A5SFY83U4'
setRank          = Classes.setRank()
epicRank         = Classes.epicRank()
itemAuctionPrice = Classes.itemAuctionPrice()

### 이벤트 ###
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('!도움말'))
    print('[알림][시크봇이 성공적으로 구동됬습니다.]')

@bot.event
async def on_message(msg):
    if msg.author.bot: return None
    await bot.process_commands(msg)

    # 명령어 사용 빈도수 저장
    Admin.saveCmdStatistics(msg)

### 검색 명령어 ###
@bot.command()
async def 등급(ctx):
    await Search.등급(ctx)

@bot.command()
async def 캐릭터(ctx, name='None', server='전체'):
    await Search.캐릭터(bot, ctx, name, server)

@bot.command()
async def 장비(ctx, *input):
    await Search.장비(bot, ctx, *input)

@bot.command()
async def 세트(ctx, *input):
    await Search.세트(bot, ctx, *input)

@bot.command()
async def 시세(ctx, *input):
    await Search.시세(ctx, itemAuctionPrice, *input)

# @bot.command()
# async def 버프력(ctx, name='None', server='전체'):
#     await Search.버프력(bot, ctx, name, server)

### 랭킹 명령어 ###
@bot.command()
async def 획득에픽(ctx, name='None', server='전체'):
    await Ranking.획득에픽(bot, ctx, epicRank, name, server)

@bot.command()
async def 기린랭킹(ctx):
    await Ranking.기린랭킹(ctx, epicRank)

### 기타 명령어 ###
@bot.command()
async def 도움말(ctx):
    await Etc.도움말(ctx)

@bot.command()
async def 명령어(ctx):
    await Etc.도움말(ctx)

@bot.command()
async def 청소(ctx):
    await Etc.청소(bot, ctx)

### 어드민 명령어 ###
@bot.command()
async def 연결(ctx):
    await Admin.연결(bot, ctx)

@bot.command()
async def 상태(ctx, *state):
    await Admin.상태(bot, ctx, *state)

@bot.command()
async def 통계(ctx):
    await Admin.통계(ctx)

bot.remove_command('help')
bot.run(token)
