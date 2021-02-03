import discord

async def 도움말(ctx):
    await ctx.message.delete()
    embed = discord.Embed(title='시크봇의 명령어들을 알려드릴게요!', description='최근 업데이트 날짜 : 2021/02/03')
    embed.add_field(name='> !등급',
                    value='오늘의 장비 등급을 알려드릴게요.\r\n'
                          '오늘 등급과 최대치와의 차이도 알려드려요.')
    embed.add_field(name="> !캐릭터 '닉네임'",
                    value='해당 캐릭터가 장착 중인 장비와 세트를 알려드릴게요.\r\n'
                          '캐릭터의 프로필 사진도 빼놓지않고 가져올게요!')
    embed.add_field(name="> !장비 '장비아이템이름'",
                    value='해당 장비 아이템의 옵션을 알려드릴게요.\r\n'
                          '결과창에서 ❤️이모지를 누르면 버퍼 전용 옵션을 볼 수 있어요.')
    embed.add_field(name="> !세트 '세트아이템이름'",
                    value='해당 세트 아이템의 옵션을 알려드릴게요.\r\n'
                          '결과창에서 ❤️이모지를 누르면 버퍼 전용 옵션을 볼 수 있어요.')
    embed.add_field(name="> !시세 '아이템이름'",
                    value='해당 아이템의 시세와 가격 변동률을 알려드릴게요.\r\n'
                          '가격 변동률은 데이터에 있는 가장 최근 날짜와 비교해서 알려드려요.')
    embed.add_field(name="> !획득에픽 '닉네임'",
                    value='해당 캐릭터가 이번 달에 획득한 에픽을 알려드릴게요.\r\n'
                          '이 명령어를 사용하면 결과가 기린랭킹에 반영되요.')
    embed.add_field(name='> !기린랭킹',
                    value='이번 달에 에픽을 많이 획득한 기린들을 박제해놨어요!\r\n'
                          '기린랭킹은 !획득에픽을 사용한 캐릭터들 중 상위 15명을 보여줘요.')
    embed.add_field(name='> !청소', value='시크봇이 말한 것들을 모두 삭제할게요.')
    await ctx.channel.send(embed=embed)
    await ctx.channel.send('> 명령어들의 더 자세한 사용법은 https://bit.ly/3jaHYcy 에서 확인할 수 있어요!')

async def 청소(bot, ctx):
    await ctx.message.delete()
    def check(m): return m.author == bot.user
    await ctx.channel.purge(check=check)
