import discord
from Src import Util

ownerId = 247361856904232960

async def 상태(bot, ctx, *input):
    if ctx.message.author.id == ownerId:
        state = ' '.join(input)
        await bot.change_presence(status=discord.Status.online, activity=discord.Game(state))
        await ctx.message.delete()
        await ctx.channel.send("> '" + state + " 하는 중' 으로 상태를 바꿨습니다.")

async def 연결(bot, ctx):
    if ctx.message.author.id == ownerId:
        await ctx.message.delete()
        await ctx.channel.send('> 시크봇은 ' + str(len(bot.guilds)) + '개의 서버에 연결되어있어요!')
