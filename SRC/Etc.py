import discord

async def 도움말(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title='시크봇의 명령어들을 알려드릴게요!', description='최근 업데이트 날짜 : 2021/02/05')
    embed.add_field(name='> !등급',
                    value='오늘의 장비 등급을 알려드릴게요.')
    embed.add_field(name="> !캐릭터 '닉네임'",
                    value='해당 캐릭터가 장착 중인 장비와 세트를 알려드릴게요.')
    embed.add_field(name="> !장비 '장비아이템이름'",
                    value='해당 장비 아이템의 옵션을 알려드릴게요')
    embed.add_field(name="> !세트 '세트아이템이름'",
                    value='해당 세트 아이템의 옵션을 알려드릴게요.')
    embed.add_field(name="> !시세 '아이템이름'",
                    value='해당 아이템의 시세와 가격 변동률을 알려드릴게요.')
    embed.add_field(name="> !획득에픽 '닉네임'",
                    value='해당 캐릭터가 이번 달에 획득한 에픽을 알려드릴게요.')
    embed.add_field(name='> !기린랭킹',
                    value='이번 달에 에픽을 많이 획득한 기린들을 박제해놨어요!')
    embed.add_field(name='> !주식',
                    value='자신이 보유하고 있는 골드와 주식을 알려드려요.')
    embed.add_field(name="> !주식매수 '아이템이름'", value='해당 아이템을 구매할 수 있어요.')
    embed.add_field(name="> !주식매도", value='보유하고 있는 주식을 매도할 수 있어요.')
    embed.add_field(name="> !주식랭킹", value='보유금과 평가금을 합친 것을 기준으로한 랭킹을 보여드려요.')
    embed.add_field(name="> !출석", value='매일마다 주식을 구매할 수 있는 골드를 얻을 수 있어요.')
    embed.add_field(name='> !청소', value='시크봇이 말한 것들을 모두 삭제할게요.')
    await ctx.channel.send(embed=embed)
    await ctx.channel.send('> 명령어들의 상세한 사용법은 https://bit.ly/3jaHYcy 에서 확인할 수 있어요!')

async def 청소(bot, ctx):
    await ctx.message.delete()
    def check(m): return m.author == bot.user
    await ctx.channel.purge(check=check)
