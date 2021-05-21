import discord
from datetime import datetime
from Database import Tool
from Src import Util

async def 출석(ctx):
    await ctx.message.delete()
    did, name = str(ctx.message.author.id), ctx.message.author.display_name
    waiting = await ctx.channel.send(f'> {name}님의 출석을 확인하고있어요...')

    account = Tool.getAccount(did)
    if account is None:
        Tool.iniAccount(did)
        account = Tool.getAccount(did)
    today = datetime.now().strftime('%Y-%m-%d')
    embed = discord.Embed(title=f'{name}님의 출석을 진행할게요!')
    embed.add_field(name='> 출석 날짜', value=today)

    # 이미 출석한 경우
    if str(account['checkDate']) == today:
        embed.add_field(name='> 출석 보상', value='X')
        embed.set_footer(text='이미 출석체크를 했어요.')
        check = False
    else:
        Tool.updateAccountCheck(did)
        reward = Util.getDailyReward()
        Tool.gainGold(did, reward)
        check = True

        embed.add_field(name='> 출석 보상', value=format(reward, ',') + '골드')
        embed.set_footer(text='출석체크 완료!')

    embed.add_field(name='> 출석 일수', value=f"{account['checkCount'] + check}일")

    await waiting.delete()
    await ctx.channel.send(embed=embed)
