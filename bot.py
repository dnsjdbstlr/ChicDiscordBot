# 디스코드
import discord
from discord.ext import commands

# API
import DNFAPI

# 기타
import Util
import Classes
from datetime import datetime

### 기본설정 ###
bot = commands.Bot(command_prefix='!')
#token = 'NzgyMTc4NTQ4MTg1NTYzMTQ3.X8Iaig.0o0wUqoz8j_iub3SC7A5SFY83U4'
token = 'NzgxNzgyNzQ5NDc5Njk4NDQy.X8Cp7A.wJ69VOJUvfEMnv6-F63QG8KNans'
epic = Classes.epicRank()

### 이벤트 ###
@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('!도움말'))
    print('구동 완료')

@bot.event
async def on_message(msg):
    if msg.author.bot:
        return None
    await bot.process_commands(msg)

### 명령어 ###
@bot.command()
async def 도움말(ctx):
    await ctx.channel.purge(limit=1)
    await ctx.channel.send("```cs\r\n" +
                           "#최근 업데이트 날짜 : 2020/12/20\r\n"
                           "#시크봇의 명령어들을 알려드릴게요!\r\n"
                           "'!등급' : 오늘의 장비 등급을 알려드릴게요.\r\n"
                           "'!캐릭터 <닉네임>' : 캐릭터가 장착한 장비와 세트를 알려드릴게요.\r\n"
                           "'!획득에픽 <닉네임>' : 캐릭터가 이번 달에 획득한 에픽을 알려드릴게요.\r\n"
                           "'!기린랭킹' : 이번 달에 에픽을 많이 먹은 기린을 박제해놨어요! 나만운업서!\r\n"
                           "'!장비 <장비아이템이름>' : 궁금하신 장비템의 옵션을 검색해서 알려드릴게요.\r\n"
                           "'!세트 <세트아이템이름>' : 궁금하신 세트템의 옵션을 검색해서 알려드릴게요.\r\n"
                           "```")

@bot.command()
async def 등급(ctx):
    itemName, itemGradeName, itemGradeValue = DNFAPI.getShopItemInfo('10f619989d70a8f21b6dd8da40f48faf')
    _itemName, _itemGradeName, _itemGradeValue = DNFAPI.getShopItemInfo('0b71d3990dd08a6945cff1dd5d1b20bb')
    __itemName, __itemGradeName, __itemGradeValue = DNFAPI.getShopItemInfo('675a13e96276653391a845e041d3acf9')

    embed = discord.Embed(title='오늘의 아이템 등급을 알려드릴게요!')
    embed.add_field(name='> ' + itemName, value=itemGradeName + '(' + str(itemGradeValue) + '%)')
    embed.add_field(name='> ' + _itemName, value=_itemGradeName + '(' + str(_itemGradeValue) + '%)')
    embed.add_field(name='> ' + __itemName, value=__itemGradeName + '(' + str(__itemGradeValue) + '%)')

    if itemGradeName == '최하급':
        footer = '오늘 하루는 절대 정가 금지!'
    elif itemGradeName == '하급':
        footer = '아무리 그래도 하급은 아니죠...'
    elif itemGradeName == '중급':
        footer = '중급...도 조금 그래요.'
    elif itemGradeName == '상급':
        footer = '조금 아쉬운데, 급하다면 어쩔 수 없어요!'
    elif itemGradeName == '최상급':
        footer = '오늘만을 기다려왔어요!!'
    embed.set_footer(text=footer)

    await ctx.channel.purge(limit=1)
    await ctx.channel.send(embed=embed)

@bot.command()
async def 캐릭터(ctx, name='None'):
    if name == 'None':
        await ctx.channel.send('> !캐릭터 <닉네임> 의 형태로 적어야해요!')
        return

    # 검색
    try:
        chrIdList = DNFAPI.getChrIdList('전체', name)
        server, chrId, name = await Util.getSelectionFromChrIdList(bot, ctx, chrIdList)
    except:
        return False

    chrEquipItemList, chrEquipItemEnchantInfo = DNFAPI.getChrEquipItemInfoList(server, chrId)
    chrEquipSetItemInfo = DNFAPI.getChrEquipSetItemInfo(chrEquipItemList)

    chrEquipSetItemName = []
    for i in chrEquipSetItemInfo:
        if i[2] is not None:
            chrEquipSetItemName.append(i[2])

    # 몇 세트 장착 중인지
    chrEquipSetItemAmount = {}
    for i in chrEquipSetItemName:
        SET = 0
        if chrEquipSetItemAmount.get(i) is not None:
            SET = chrEquipSetItemAmount.get(i)
        chrEquipSetItemAmount.update({i : SET + 1})

    # 세트이름만 추출
    chrEquipSetItemName = list(set(chrEquipSetItemName))

    # embed 설정
    embed = discord.Embed(title=name + '님의 캐릭터 정보를 알려드릴게요.')
    embed.set_image(url='https://img-api.neople.co.kr/df/servers/' + DNFAPI.SERVER_ID[server] + '/characters/' + chrId + '?zoom=1')

    # 필드 추가
    value = ''
    for i in chrEquipSetItemName:
        value += i + '(' + str(chrEquipSetItemAmount.get(i)) + ')\r\n'
    if value != '':
        embed.add_field(name='> 장착중인 세트', value=value, inline=False)

    # 장비 옵션
    for i in range(len(chrEquipSetItemInfo)):
        value = ''
        reinforce = chrEquipItemEnchantInfo[i]['reinforce']
        refine = chrEquipItemEnchantInfo[i]['refine']
        if reinforce != 0:
            value += '+' + str(chrEquipItemEnchantInfo[i]['reinforce'])
        if refine != 0:
            value += '(' + str(chrEquipItemEnchantInfo[i]['refine']) + ')'
        value += ' ' + chrEquipSetItemInfo[i][1] + '\r\n'
        try:
            value += chrEquipItemEnchantInfo[i]['enchant']
        except: pass
        embed.add_field(name='> ' + chrEquipSetItemInfo[i][0], value=value)

    # 푸터
    embed.set_footer(text=name + '님의 캐릭터 이미지도 챙겨왔어요!')
    await ctx.channel.send(embed=embed)

# @bot.command()
# async def 상세정보(ctx, name='None'):
#     if name == 'None':
#         await ctx.channel.send('> !캐릭터 <닉네임> 의 형태로 적어야해요!')
#         return
#
#     # 검색
#     try:
#         chrIdList = DNFAPI.getChrIdList('전체', name)
#         server, chrId, name = await Util.getSelectionFromChrIdList(bot, ctx, chrIdList)
#     except:
#         return False
#
#     itemIdList = DNFAPI.getChrEquipItemIdList(server, chrId)
#     chrEquipCreatureId = DNFAPI.getChrEquipCreatureId(server, chrId)
#     itemIdList.append(chrEquipCreatureId)
#
#     ### 정규식 설정 ###
#     rDmgInc       = re.compile('공격 시 데미지 (?P<value>\d+)% 증가')
#     rCriDmgInc    = re.compile('크리티컬 공격 시 데미지 (?P<value>\d+)% 증가')
#     rAddDmgInc    = re.compile('공격 시 데미지 증가량 (?P<value>\d+)% 추가 증가')
#     rAddCriDmgInc = re.compile('크리티컬 공격 시 데미지 증가량 (?P<value>\d+)% 추가 증가')
#     rAddDmg       = re.compile('공격 시 (?P<value>\d+)% 추가 데미지')
#     rEleAddDmg    = re.compile('공격 시 (?P<value>\d+)% 속성 추가 데미지')
#     rSkillDmgInc  = re.compile('스킬 공격력 (?P<value>\d+)% 증가')
#     ### 정규식 설정 끝 ###
#
#     ### 변수 설정 ###
#     dmgInc       = 0 # 데미지 증가
#     addDmgInc    = 0 # 데미지 추가 증가
#     criDmgInc    = 0 # 크리티컬 데미지 증가
#     addCriDmgInc = 0 # 크리티컬 데미지 추가 증가
#     addDmg       = 0 # 추가 데미지
#     eleAddDmg    = 0 # 속성 추가 데미지
#     allDmgInc    = 0 # 모든 공격력 증가
#     skillDmgInc  = 1 # 스킬 데미지 증가
#     adApInInc    = 0 # 물리,마법, 독립 공격력 증가
#     ### 선언 끝 ###
#
#     for itemId in itemIdList:
#         itemDetailInfo = DNFAPI.getItemDetail(itemId)
#         info = itemDetailInfo['itemExplainDetail'].split('\n')
#
#         # 신화 옵션
#         try:
#             for i in itemDetailInfo['mythologyInfo']['options']:
#                 info.append(i['explain'])
#         except: pass
#
#         for i in info:
#             # 데미지, 크리티컬 데미지 증가
#             tCriDmgInc = rCriDmgInc.search(i)
#             if tCriDmgInc is not None and criDmgInc < int(tCriDmgInc.group('value')):
#                 criDmgInc = int(tCriDmgInc.group('value'))
#             else:
#                 tDmgInc = rDmgInc.search(i)
#                 if tDmgInc is not None and dmgInc < int(tDmgInc.group('value')):
#                     dmgInc = int(tDmgInc.group('value'))
#
#             # 데미지, 크리티컬 데미지 추가 증가
#             tAddCriDmgInc = rAddCriDmgInc.search(i)
#             if tAddCriDmgInc is not None:
#                 addCriDmgInc += int(tAddCriDmgInc.group('value'))
#             else:
#                 tAddDmgInc = rAddDmgInc.search(i)
#                 if tAddDmgInc is not None:
#                     addDmgInc += int(tAddDmgInc.group('value'))
#
#             # 추가 데미지
#             tAddDmg = rAddDmg.search(i)
#             if tAddDmg is not None:
#                 addDmg += int(tAddDmg.group('value'))
#
#             # 속성 추가 데미지
#             tEleDmg = rEleAddDmg.search(i)
#             if tEleDmg is not None:
#                 eleAddDmg += int(tEleDmg.group('value'))
#
#             # 스킬 데미지 증가
#             tSkillDmgInc = rSkillDmgInc.search(i)
#             if tSkillDmgInc is not None:
#                 skillDmgInc *= 1 + int(tSkillDmgInc.group('value')) / 100
#
#     # 속성 추가 데미지 계산
#     chrStatInfo = DNFAPI.getChrStatInfo(server, chrId)
#     r = re.compile('\S속성 강화')
#     element = 0
#     for i in chrStatInfo:
#         temp = r.search(i['name'])
#         if temp is not None:
#             value = i['value']
#             if value > element:
#                 element = value
#     eleAddDmg = int(eleAddDmg * (1.05 + 0.0045 * element))
#
#     # 스킬 데미지 계산
#     skillDmgInc = int((skillDmgInc - 1) * 100)
#     if skillDmgInc == 1:
#         skillDmgInc = 0
#
#     embed = discord.Embed(title=name + '님의 상세정보를 알려드릴게요.', description='능력치에 따른 효율도 알려드릴게요!')
#     embed.add_field(name='> 데미지 증가',          value=str(dmgInc + addDmgInc) + '%')
#     embed.add_field(name='> 크리티컬 데미지 증가', value=str(criDmgInc + addCriDmgInc) + '%')
#     embed.add_field(name='> 추가 데미지',          value=str(addDmg) + '% + ' + str(eleAddDmg) + '%')
#     embed.add_field(name='> 스킬 데미지 증가',     value=str(skillDmgInc) + '%')
#     embed.set_footer(text='이 수치들은 모두 극옵션으로 계산한거예요!')
#     await ctx.channel.send(embed=embed)

@bot.command()
async def 획득에픽(ctx, name='None'):
    if name == 'None':
        await ctx.channel.send('> !획득에픽 <닉네임> 의 형태로 적어야해요!')
        return

    # 검색
    try:
        chrIdList = DNFAPI.getChrIdList('전체', name)
        server, chrId, name = await Util.getSelectionFromChrIdList(bot, ctx, chrIdList)
    except:
        return False

    chrTimeLineData = DNFAPI.getChrTimeLine(server, chrId, '505')
    if len(chrTimeLineData) == 0:
        await ctx.channel.send('> ' + name + '님은 이번 달 획득한 에픽이 없어요.. ㅠㅠ')
        return

    # 결과 출력
    # 15개씩 나눠서 출력
    index = 0
    while index < len(chrTimeLineData):
        start = index
        end   = min(start + 15, len(chrTimeLineData))
    
        if start == 0:
            embed = discord.Embed(title=name + '님이 이번 달에 획득한 에픽을 알려드릴게요!',
                                  description='총 ' + str(len(chrTimeLineData)) + '개의 에픽을 획득하셨네요!')
        else:
            embed = discord.Embed(title=str(start + 1) + ' ~ ' + str(end) + '번째 획득한 에픽들')
    
        for i in chrTimeLineData[start:end]:
            embed.add_field(name='> ' + i['date'][:10] + '\r\n> ch' + str(i['data']['channelNo']) + '.' + i['data']['channelName'], value=i['data']['itemName'])
        await ctx.channel.send(embed=embed)

        index += 15

    # 데이터 저장
    today = datetime.today()
    epic.add(chrId, [today.year, today.month, server, name, len(chrTimeLineData)])

@bot.command()
async def 기린랭킹(ctx):
    today = datetime.today()
    epic.update(today.month)
    embed = discord.Embed(title=str(today.year) + '년 ' + str(today.month) + '월 기린 랭킹을 알려드릴게요!', description='랭킹은 매달 초기화되며 15등까지만 보여드려요.')
    embed.set_footer(text='열심히 개발중이라 랭킹이 자주 초기화될 수 있어요.')

    rank = 1
    for k in epic.data.keys():
        name  = '> ' + str(rank) + '등\r\n> ' + epic.data[k][2] + ' ' + epic.data[k][3]
        value = '에픽 ' + str(epic.data[k][4]) + '개 획득!'
        embed.add_field(name=name, value=value)
        rank += 1

    if rank == 1:
        embed.add_field(name='> 랭킹에 아무도 없어요!', value='> !획득에픽 <닉네임> 으로 자신의 캐릭터를 랭킹에 추가해보세요!')

    await ctx.channel.purge(limit=1)
    await ctx.channel.send(embed=embed)

@bot.command()
async def 장비(ctx, *input):
    name = ''
    for i in input: name += i + ' '
    name = name.rstrip()

    if len(name) < 1:
        await ctx.channel.send('> !장비 <장비템이름> 의 형태로 적어야해!')
        return

    # 해당 정보가 있는지 체크
    hasItemSkillLvInfo = True
    hasItemMythicInfo  = True

    # 아이템 id 얻어오기
    try:
        itemIdList = DNFAPI.getItemId(name)
        itemId = await Util.getSelectionFromItemIdList(bot, ctx, itemIdList)
        if itemId is False: return
    except:
        return
    ### 선택 종료 ###

    itemDetailInfo = DNFAPI.getItemDetail(itemId)
    itemImageUrl   = DNFAPI.getItemImageUrl(itemId)

    # 스탯
    itemStatInfo = DNFAPI.getItemStatInfo(itemDetailInfo['itemStatus'])

    # 스킬 레벨
    try:
        itemSkillLvInfo = DNFAPI.getItemSkillLvInfo(itemDetailInfo['itemReinforceSkill'][0]['jobName'],
                                                    itemDetailInfo['itemReinforceSkill'][0]['levelRange'])
    except: hasItemSkillLvInfo = False
    
    # 신화옵션
    try:
        itemMythicInfo = DNFAPI.getItemMythicInfo(itemDetailInfo['mythologyInfo']['options'])
    except: hasItemMythicInfo = False

    # 플레이버 텍스트
    itemFlavorText = itemDetailInfo['itemFlavorText']

    # 출력
    embed = discord.Embed(title=itemDetailInfo['itemName'],
                          description=str(itemDetailInfo['itemAvailableLevel']) + 'Lv ' + itemDetailInfo['itemRarity'] + ' ' + itemDetailInfo['itemTypeDetail'])
    embed.add_field(name='> 스탯', value=itemStatInfo, inline=False)
    if hasItemSkillLvInfo:
        embed.add_field(name='> 스킬', value=itemSkillLvInfo)
    embed.add_field(name='> 옵션', value=itemDetailInfo['itemExplainDetail'], inline=False)
    if hasItemMythicInfo:
        embed.add_field(name='> 신화옵션', value=itemMythicInfo, inline=False)
    embed.set_footer(text=itemFlavorText)
    embed.set_thumbnail(url=itemImageUrl)

    await ctx.channel.send(embed=embed)

@bot.command()
async def 세트(ctx, *input):
    setItemName = ''
    for i in input:
        setItemName += i + ' '
    setItemName = setItemName.rstrip()

    if len(setItemName) < 1:
        await ctx.channel.send('> !세트 <세트옵션이름> 의 형태로 적어야해!')
        return

    try:
        setItemIdList = DNFAPI.getSetItemIdList(setItemName)
        setItemId, setItemName = await Util.getSelectionFromSetItemIdList(bot, ctx, setItemIdList)
    except:
        return

    setItemInfoList, setItemOptionList = DNFAPI.getSetItemInfoList(setItemId)
    embed2 = discord.Embed(title=setItemName + '의 정보를 알려드릴게요.')
    for i in setItemInfoList:
        embed2.add_field(name='> ' + i['itemRarity'] + ' ' + i['slotName'], value=i['itemName'] + '\r\n')
    for i in setItemOptionList:
        embed2.add_field(name='> ' + str(i['optionNo']) + '세트 옵션', value=i['explain'])
    itemImageUrl = DNFAPI.getItemImageUrl(setItemInfoList[0]['itemId'])
    embed2.set_thumbnail(url=itemImageUrl)

    await ctx.channel.send(embed=embed2)

### 제작자 명령어 ###
@bot.command()
async def 연결(ctx):
    if ctx.message.author.id == 247361856904232960:
        await ctx.channel.purge(limit=1)
        NUMBER_OF_CONNECTED_SERVER = len(bot.guilds)

        index = 0
        while index < NUMBER_OF_CONNECTED_SERVER:
            start = index
            end   = min(len(bot.guilds), index + 15)
            
            if start == 0:
                title = str(NUMBER_OF_CONNECTED_SERVER) + '개의 서버에 시크봇이 연결되어있어요!\r\n' + str(start + 1) + ' ~ ' + str(end) + '번째 서버 목록'
            else:
                title = str(start + 1) + ' ~ ' + str(end) + '번째 서버 목록'
            embed = discord.Embed(title=title)
            
            # 출력
            for i in bot.guilds[start:end]:
                embed.add_field(name='> ' + i.name, value=str(i.member_count) + '명')
            await ctx.channel.send(embed=embed)

            index += 15

@bot.command()
async def 상태(ctx, *state):
    if ctx.message.author.id == 247361856904232960:
        _state = ''
        for i in state:
            _state += i + ' '
        _state = _state.rstrip()

        await bot.change_presence(status=discord.Status.online, activity=discord.Game(_state))
        await ctx.channel.purge(limit=1)
        await ctx.channel.send("> '" + _state + "하는 중' 으로 상태를 바꿨습니다.")

bot.remove_command('help')
bot.run(token)
