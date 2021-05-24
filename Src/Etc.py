import discord

async def 도움말(bot, ctx):
    def MAKE_EMBED(ePage):
        if ePage == 1:
            eTitle = "시크봇의 `검색` 관련 명령어들을 알려드릴게요!"
        elif ePage == 2:
            eTitle = "시크봇의 `선물거래` 관련 명령어들을 알려드릴게요!"
        elif ePage == 3:
            eTitle = "시크봇의 `강화` 관련 명령어들을 알려드릴게요!"
        elif ePage == 4:
            eTitle = "시크봇의 `기타` 명령어들을 알려드릴게요!"
        else:
            eTitle = "오류"
        eEmbed = discord.Embed(title=eTitle)

        if ePage == 1:
            eEmbed.add_field(name='> !등급', inline=False,
                             value='오늘의 장비 등급을 알려드릴게요. 100% 장비와 비교해서 어느 스탯이 부족한지도 알려드려요!\n'
                                   'ex) `!등급`')
            eEmbed.add_field(name="> !캐릭터 <서버> <닉네임>", inline=False,
                             value='해당 캐릭터가 장착 중인 아이템과 아바타 알려드릴게요.\n'
                                   '<서버>는 생략할 수 있고 생략하지 않으면 해당 서버의 캐릭터만 검색해요.\n'
                                   'ex) `!캐릭터 로리장인시크`, `!캐릭터 바칼 배메장인시크`')
            eEmbed.add_field(name="> !장비 <장비아이템이름>", inline=False,
                             value='해당 장비 아이템의 옵션을 알려드릴게요.\n'
                                   '장비아이템 이름은 정확하지 않아도되요. 검색 결과 중에서 원하는 장비를 선택하면되요.\n'
                                   'ex) `!장비 세계수의 요정`, `!장비 선택`')
            eEmbed.add_field(name="> !세트 <세트아이템이름>", inline=False,
                             value='해당 세트 아이템의 옵션을 알려드릴게요.\n'
                                   '세트아이템 이름은 정확하지 않아도되요. 검색 결과 중에서 원하는 세트를 선택하면되요.\n'
                                   'ex) `!세트 선택의 기로 세트`, `!세트 개악`')
            eEmbed.add_field(name="> !시세 <아이템이름>", inline=False,
                             value='해당 아이템의 시세와 가격 변동률을 알려드릴게요.\n'
                                   '아이템이름은 최대한 정확해야 검색할 수 있어요.\n'
                                   'ex) `!시세 아이올라이트`, `!시세 시간의 결정`')
            eEmbed.add_field(name="> !에픽 <서버> <닉네임>", inline=False,
                             value='해당 캐릭터가 이번 달에 획득한 에픽의 정보를 알려드릴게요.\n'
                                   '<서버>는 생략할 수 있고 생략하지 않으면 해당 서버의 캐릭터만 검색해요.\n'
                                   'ex) `!에픽 로리장인시크`, `!에픽 바칼 배메장인시크`')
            eEmbed.add_field(name='> !에픽랭킹', inline=False,
                             value='이번 달 획득한 에픽 개수를 기준으로한 랭킹을 보여드려요.\n'
                                   'ex) `!에픽랭킹`')

        elif ePage == 2:
            eEmbed.add_field(name='> !선물거래', inline=False,
                             value='던파 경매장을 기반으로한 선물 거래에 대한 설명을 알려드려요.\n'
                                   'ex) `!선물거래`')
            eEmbed.add_field(name="> !주문 <종목> <레버리지>", inline=False,
                             value='해당 포지션의 주문을 넣어요. 종목에는 다음의 6개의 아이템만 가능해요.\n'
                                   '`아이올라이트`, `시간의 결정`, `고대 지혜의 잔해`,\n'
                                   '`힘의 정수 1개 상자`, `무색 큐브 조각`, `모순의 결정체`\n'
                                   'ex) `!주문 아이올라이트 10`, `!주문 시간의 결정 -10')
            eEmbed.add_field(name="> !포지션", inline=False,
                             value='현재 보유 중인 포지션을 확인할 수 있어요.\n'
                                   '또한 자신이 원하는 포지션의 이모지를 눌러서 포지션을 종료할 수 있어요.\n'
                                   'ex) `!포지션`')
            eEmbed.add_field(name="> !거래내역", inline=False,
                             value='최근 6번의 선물 거래 내역과 그에 따른 총 손익을 알려드려요.\n'
                                   'ex) `!거래내역`')
            eEmbed.add_field(name="> !파산", inline=False,
                             value='파산을 신청해요. 골드와 포지션이 모두 사라지고 하루동안 선물 거래를 할 수 없어요.\n'
                                   'ex) `!파산`')
            eEmbed.add_field(name="> !골드랭킹", inline=False,
                             value='보유금과 평가금을 합한 것을 기준으로한 랭킹을 보여드려요.\n'
                                   'ex) `!골드랭킹`')

        elif ePage == 3:
            eEmbed.add_field(name="> !강화 <무기아이템이름>", inline=False,
                             value='무기아이템이름을 적으면 `!강화` 명령어를 사용할 때 강화할 무기를 설정해요.\n'
                                   '강화할 무기가 설정되어 있어야 강화를 할 수 있어요.\n'
                                   'ex) `!강화 세계수의 요정`, `!강화`')
            eEmbed.add_field(name="> !강화내역", inline=False,
                             value='현재 설정된 무기와 여태 최고 강화 수치, 강화 성공, 실패, 파괴 횟수를 알려드려요.\n'
                                   'ex) `!강화내역`')
            eEmbed.add_field(name="> !공개강화", inline=False,
                             value='다른 사람들에게 골드를 기부받을 수 있는 강화예요.\n'
                                   '강화할 무기가 설정되어 있어야 `!공개강화` 명령어를 사용할 수 있어요.\n'
                                   'ex) `!공개강화`')
            eEmbed.add_field(name="> !강화랭킹", inline=False,
                             value='최고 강화 수치를 기준으로한 랭킹을 보여드려요.\n'
                                   'ex) `!강화랭킹`')

        elif ePage == 4:
            eEmbed.add_field(name="> !출석", inline=False,
                             value='매일마다 랜덤한 골드를 얻을 수 있어요. 추후 더 많은 효과가 추가될 수 있어요!\n'
                                   'ex) `!출석`, `!출첵`, `!출석체크`')
            eEmbed.add_field(name='> !청소', inline=False,
                             value='시크봇이 말한 것들을 모두 삭제해요.\n'
                                   'ex) `!청소`')
            eEmbed.add_field(name='> #시크봇', inline=False,
                             value='채널 주제에 이 태그가 있는 채팅 채널에서만 사용 가능해요.\n'
                                   '모든 채널에 해당 태그가 없다면 시크봇을 모든 채팅 채널에서 사용할 수 있어요.\n'
                                   'ex) 채널 편집 -> 채널 주제 -> `#시크봇` 추가')
            eEmbed.add_field(name='> 더 자세한 설명', inline=False,
                             value='[여기에서 확인할 수 있어요.](https://blog.naver.com/dnsjdbstlr/222158093456)')
            eEmbed.add_field(name='> 1윤시크 :: 커뮤니티', inline=False,
                             value='던파와 코딩과 관련된 디스코드 커뮤니티예요!\n'
                                   '던파와 디스코드봇에 관심이 있으신 분이라면 들어오면 좋을 것 같아요!\n'
                                   '[여기를 누르면 초대받을 수 있어요.](https://discord.gg/ZUbjgY4jg2)')
        eEmbed.set_footer(text=f'{ePage}페이지 / 4페이지')
        return eEmbed
    
    await ctx.message.delete()

    page = 1
    msg = await ctx.channel.send(embed=MAKE_EMBED(page))
    await msg.add_reaction('▶️')

    while True:
        try:
            def check(_reaction, _user):
                return str(_reaction) in ['◀️', '▶️'] and _user.id == ctx.author.id and _reaction.message.id == msg.id
            reaction, user = await bot.wait_for('reaction_add', check=check)

            if str(reaction) == '◀️' and page > 1:
                page -= 1
            if str(reaction) == '▶️' and page < 4:
                page += 1

            await msg.edit(embed=MAKE_EMBED(page))
            await msg.clear_reactions()
            if page > 1:
                await msg.add_reaction('◀️')
            if page < 4:
                await msg.add_reaction('▶️')
        except: return

async def 청소(bot, ctx):
    def check(message): return message.author == bot.user
    await ctx.channel.purge(check=check)
    await ctx.message.delete()
