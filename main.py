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

# # # 광 부 # # #
@bot.command()
async def 출석(ctx):
    await stock.출석(ctx)

@bot.command()
async def 출석체크(ctx):
    await stock.출석(ctx)

@bot.command()
async def 광부(ctx):
    name, did = ctx.message.author.display_name, ctx.message.author.id
    
    await ctx.message.delete()
    embed = discord.Embed(title=f"{name}님의 광부", description=f"원하시는 구역을 선택해주세요. 끝나면 DM으로 알려드릴게요!")
    embed.add_field(name='> 재난구역',      value='소요시간 : 30분\r\n보상 : 300,000 ~ 500,000골드')
    embed.add_field(name='> 마계대전',      value='소요시간 : 1시간\r\n보상 : 500,000 ~ 750,000골드')
    embed.add_field(name='> 폭풍의 항로',   value='소요시간 : 3시간\r\n보상 : 750,000 ~ 1,000,000골드')
    embed.add_field(name='> 더 오큘러스',   value='소요시간 : 6시간\r\n보상 : 1,000,000 ~ 1,500,000골드')
    embed.add_field(name='> 추방자의 산맥', value='소요시간 : 12시간\r\n보상 : 1,500,000 ~ 2,000,000골드')
    embed.add_field(name='> 검은연옥',      value='소요시간 : 24시간\r\n보상 : 3,000,000 ~ 5,000,000골드')
    message = await ctx.channel.send(embed=embed)
    await message.add_reaction('1️⃣')
    await message.add_reaction('2️⃣')
    await message.add_reaction('3️⃣')
    await message.add_reaction('4️⃣')
    await message.add_reaction('5️⃣')
    await message.add_reaction('6️⃣')

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
