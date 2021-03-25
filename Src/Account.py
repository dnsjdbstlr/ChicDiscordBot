import discord
from datetime import datetime
from Database import Tool
from Src import Util

async def 출석(ctx):
    await ctx.message.delete()
    did, name = str(ctx.message.author.id), ctx.message.author.display_name
    waiting = await ctx.channel.send(f'> {name}님의 출석을 확인하고있어요...')

    # 출석 체크 확인
    dailyCheck = Tool.getDailyCheck(did)
    today = datetime.now().strftime('%Y-%m-%d')
    if dailyCheck is not None and str(dailyCheck.get('date')) == today:
        embed = discord.Embed(title=f'{name}님의 출석체크')
        embed.add_field(name='> 출석 날짜', value=today)
        embed.add_field(name='> 출석 일수', value=f"{dailyCheck['count']}일")
        embed.add_field(name='> 출석 보상', value='X')
        embed.set_footer(text='이미 출석체크를 했어요.')
        await waiting.delete()
        await ctx.channel.send(embed=embed)
        return

    # 출석 체크
    if Tool.getAccount(did) is None:
        Tool.iniAccount(did)
    reward = Util.getDailyReward()
    Tool.gainGold(did, reward)
    Tool.updateDailyCheck(did)
    dailyCheck = Tool.getDailyCheck(did)

    embed = discord.Embed(title=f'{name}님의 출석체크')
    embed.add_field(name='> 출석 날짜', value=today)
    embed.add_field(name='> 출석 일수', value=f"{dailyCheck['count']}일")
    embed.add_field(name='> 출석 보상', value=format(reward, ',') + '골드')
    embed.set_footer(text='출석체크 완료!')
    await waiting.delete()
    await ctx.channel.send(embed=embed)
