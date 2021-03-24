import discord

async def 도움말(bot, ctx):
    await ctx.message.delete()

    page = 1
    msg = await ctx.channel.send(embed=getChicBotDesc(page))
    await msg.add_reaction('▶️')

    while True:
        try:
            def check(_reaction, _user):
                return str(_reaction) in ['◀️', '▶️'] and _user == ctx.author and _reaction.message.id == msg.id
            reaction, user = await bot.wait_for('reaction_add', check=check)

            if str(reaction) == '◀️' and page > 1:
                page -= 1
            if str(reaction) == '▶️' and page < 4:
                page += 1

            await msg.edit(embed=getChicBotDesc(page))
            await msg.clear_reactions()

            if page > 1:
                await msg.add_reaction('◀️')
            if page < 4:
                await msg.add_reaction('▶️')
        except: pass

async def 청소(bot, ctx):
    def check(m): return m.author == bot.user
    await ctx.channel.purge(check=check)
    await ctx.message.delete()

def getChicBotDesc(page):
    if page == 1:
        title = "시크봇의 '검색' 관련 명령어들을 알려드릴게요!"
    elif page == 2:
        title = "시크봇의 '주식' 관련 명령어들을 알려드릴게요!"
    elif page == 3:
        title = "시크봇의 '강화' 관련 명령어들을 알려드릴게요!"
    elif page == 4:
        title = "시크봇의 '기타' 명령어들을 알려드릴게요!"
    else:
        title = "오류"
    embed = discord.Embed(title=title)
    if page == 1:
        embed.add_field(name='> !등급',                  value='오늘의 장비 등급을 알려드릴게요.')
        embed.add_field(name="> !캐릭터 '닉네임'",       value='해당 캐릭터가 장착 중인 장비와 세트를 알려드릴게요.')
        embed.add_field(name="> !장비 '장비아이템이름'", value='해당 장비 아이템의 옵션을 알려드릴게요')
        embed.add_field(name="> !세트 '세트아이템이름'", value='해당 세트 아이템의 옵션을 알려드릴게요.')
        embed.add_field(name="> !시세 '아이템이름'",     value='해당 아이템의 시세와 가격 변동률을 알려드릴게요.')
        embed.add_field(name="> !획득에픽 '닉네임'",     value='해당 캐릭터가 이번 달에 획득한 에픽을 알려드릴게요.')
        embed.add_field(name='> !기린랭킹',              value='이번 달에 에픽을 많이 획득한 기린들을 박제해놨어요!')
    elif page == 2:
        embed.add_field(name='> !주식',              value='자신이 보유하고 있는 골드와 주식을 알려드려요. 주식 관련 명령어를 사용하기 위해서 적어도 한 번은 사용해야해요.')
        embed.add_field(name="> !매수 '아이템이름'", value='해당하는 던파 아이템을 매수할 수 있어요.')
        embed.add_field(name="> !매도",              value='보유하고 있는 주식을 매도할 수 있어요.')
        embed.add_field(name="> !주식랭킹",          value='보유금과 평가금을 합친 것을 기준으로한 랭킹을 보여드려요.')
    elif page == 3:
        embed.add_field(name="> !강화설정 '무기아이템이름'", value='강화할 아이템을 설정합니다. 강화 관련 명령어를 사용하기 위해서 적어도 한 번은 사용해야해요.')
        embed.add_field(name="> !강화정보",                  value='현재 무기, 여태 최고 강화 수치 그리고 강화 시도 횟수를 알려드려요.')
        embed.add_field(name="> !강화",                      value='무기를 강화해요. 던전앤파이터 강화와 같은 시스템이예요.')
        embed.add_field(name="> !공개강화",                  value='다른 사람들에게 골드를 기부받을 수 있는 강화예요.')
    elif page == 4:
        embed.add_field(name="> !출석",               value='매일마다 골드를 얻을 수 있어요. 추후 더 많은 효과가 추가될거예요.')
        embed.add_field(name='> !청소',               value='시크봇이 말한 것들을 모두 삭제할게요.')
        embed.add_field(name='> #시크봇',             value='채널 주제에 이 태그가 있는 채팅 채널에서만 사용 가능해요.')
        embed.add_field(name='> 더 자세한 설명',      value='[여기에서 확인할 수 있어요.](https://blog.naver.com/dnsjdbstlr/222158093456)')
        embed.add_field(name='> 1윤시크 :: 커뮤니티', value='[누르면 초대받을 수 있어요.](https://discord.gg/ZUbjgY4jg2)')
    embed.set_footer(text=f'4쪽 중 {page}쪽')
    return embed