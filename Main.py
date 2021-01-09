import discord
from datetime import datetime
from discord.ext import commands
from FrameWork import Util, DNFAPI, Classes
bot = commands.Bot(command_prefix='!')

### 기본설정 ###
token = 'NzgxNzgyNzQ5NDc5Njk4NDQy.X8Cp7A.wJ69VOJUvfEMnv6-F63QG8KNans'
#token   = 'NzgyMTc4NTQ4MTg1NTYzMTQ3.X8Iaig.0o0wUqoz8j_iub3SC7A5SFY83U4'
ownerId = 247361856904232960
setRank          = Classes.setRank()
epicRank         = Classes.epicRank()
itemAuctionPrice = Classes.itemAuctionPrice()
cmdStatistics    = Classes.cmdStatistics()

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
    Util.saveCmdStatistics(cmdStatistics, msg)

### 명령어 ###
@bot.command()
async def 도움말(ctx):
    await ctx.message.delete()
    await ctx.channel.send("```cs\r\n" +
                           "#시크봇의 명령어들을 알려드릴게요!\r\n"
                           "#최근 업데이트 날짜 : 2021/01/08                    #건의사항 : LaivY#2463\r\n"
                           "──────────────────────────────────검색──────────────────────────────────\r\n"
                           "'!등급' : 오늘의 장비 등급을 알려드릴게요.\r\n"
                           "'!캐릭터 <닉네임>' : 캐릭터가 장착한 장비와 세트를 알려드릴게요.\r\n"
                           "'!시세 <아이템이름>' : 해당 아이템의 시세와 가격 변동률을 알려드릴게요.\r\n"
                           "'!장비 <장비아이템이름>' : 해당 장비아이템의 옵션을 검색해서 알려드릴게요.\r\n"
                           "'!세트 <세트아이템이름>' : 해당 세트아이템의 옵션을 검색해서 알려드릴게요.\r\n"
                           "\r\n──────────────────────────────────랭킹──────────────────────────────────\r\n"
                           "'!획득에픽 <닉네임>' : 캐릭터가 이번 달에 획득한 에픽을 알려드릴게요.\r\n"
                           #"'!상세정보 <닉네임>' : 캐릭터의 공격력 증가치를 알려드릴게요. 효율이랑요!\r\n"
                           "'!기린랭킹' : 이번 달에 에픽을 많이 먹은 기린을 박제해놨어요! 나만운업서!\r\n"
                           #"'!세팅랭킹' : 캐릭터의 상세정보를 기반으로한 세팅 점수 랭킹을 보여드릴게요.\r\n"
                           "\r\n──────────────────────────────────기타──────────────────────────────────\r\n"
                           "'!청소' : 시크봇이 말한 것들을 모두 삭제할게요.\r\n"
                           "```")

@bot.command()
async def 등급(ctx):
    await ctx.message.delete()
    waiting = await ctx.channel.send('> 오늘의 아이템 등급을 읽어오고있어요...')

    itemIdList = ['52b3fac226cfa92cba9cffff516fb06e', '55d4d2bbf302e19ea1b7bf7487f91120',
                  '10f619989d70a8f21b6dd8da40f48faf', '2230b9bb6a9d484c3f94c5721750de23',
                  '01c9dcf2c3294bec093984e3d12b87ab', '7fae76b5a3fd513001a5d40716e1287f']
    shopItemInfo = [DNFAPI.getShopItemInfo(i) for i in itemIdList]

    embed = discord.Embed(title='오늘의 아이템 등급을 알려드릴게요!')
    for i in shopItemInfo:
        embed.add_field(name='> ' + i['itemName'], value=i['itemGradeName'] + '(' + str(i['itemGradeValue']) + '%)')

    if shopItemInfo[0]['itemGradeName'] == '최하급':
        footer = '오늘 하루는 절대 정가 금지!'
    elif shopItemInfo[0]['itemGradeName'] == '하급':
        footer = '아무리 그래도 하급은 아니죠...'
    elif shopItemInfo[0]['itemGradeName'] == '중급':
        footer = '중급...도 조금 그래요.'
    elif shopItemInfo[0]['itemGradeName'] == '상급':
        footer = '조금 아쉬운데, 급하다면 어쩔 수 없어요!'
    elif shopItemInfo[0]['itemGradeName'] == '최상급':
        footer = '오늘만을 기다려왔어요!!'
    embed.set_footer(text=footer)

    await waiting.delete()
    await ctx.channel.send(embed=embed)

@bot.command()
async def 캐릭터(ctx, name='None', _server='전체'):
    if name == 'None':
        await ctx.message.delete()
        await ctx.channel.send('> !캐릭터 <닉네임> 의 형태로 적어야해요!')
        return

    # 검색
    try:
        chrIdList = DNFAPI.getChrIdList(_server, name)
        server, chrId, name = await Util.getSelectionFromChrIdList(bot, ctx, chrIdList)
    except:
        return False

    chrEquipItemList, chrEquipSetItemInfo = DNFAPI.getChrEquipItemInfoList(server, chrId)

    # embed 설정
    embed = discord.Embed(title=name + '님의 캐릭터 정보를 알려드릴게요.')
    embed.set_image(url='https://img-api.neople.co.kr/df/servers/' + DNFAPI.SERVER_ID[server] + '/characters/' + chrId + '?zoom=1')

    # 장착중인 세트
    value = ''
    for i in chrEquipSetItemInfo:
        value += i['setItemName'] + '(' + str(i['activeSetNo']) + ')\r\n'
    if value != '':
        embed.add_field(name='> 장착중인 세트', value=value, inline=False)

    # 장비 옵션
    for i in chrEquipItemList:
        if i['slotName'] in ['칭호', '보조무기']: continue

        reinforce = i['reinforce']
        refine    = i['refine']
        value = ''

        # 강화, 재련 수치
        if reinforce != 0:
            value += '+' + str(reinforce)
        if refine != 0:
            value += '(' + str(refine) + ')'
        value += ' ' + i['itemName'] + '\r\n'

        # 마법부여
        try:
            for j in i['enchant']['status']:
                value += j['name'] + ' +' + str(j['value']) + '\r\n'
        except: pass
        embed.add_field(name='> ' + i['slotName'], value=value)
    embed.set_footer(text=name + '님의 캐릭터 이미지도 챙겨왔어요!')
    await ctx.channel.send(embed=embed)

@bot.command()
async def 장비(ctx, *input):
    name = ''
    for i in input: name += i + ' '
    name = name.rstrip()

    if len(name) < 1:
        await ctx.message.delete()
        await ctx.channel.send('> !장비 <장비템이름> 의 형태로 적어야해요!')
        return

    # 해당 정보가 있는지 체크
    hasItemSkillLvInfo = True
    hasItemMythicInfo = True

    # 아이템 id 얻어오기
    try:
        itemIdList = DNFAPI.getItemId(name)
        itemId = await Util.getSelectionFromItemIdList(bot, ctx, itemIdList)
        if itemId is False: return
    except:
        return
    ### 선택 종료 ###

    itemDetailInfo = DNFAPI.getItemDetail(itemId)
    itemImageUrl = DNFAPI.getItemImageUrl(itemId)

    # 스탯
    itemStatInfo = DNFAPI.getItemStatInfo(itemDetailInfo['itemStatus'])

    # 스킬 레벨
    try:
        itemSkillLvInfo = DNFAPI.getItemSkillLvInfo(itemDetailInfo['itemReinforceSkill'][0]['jobName'],
                                                    itemDetailInfo['itemReinforceSkill'][0]['levelRange'])
    except:
        hasItemSkillLvInfo = False

    # 신화옵션
    try:
        itemMythicInfo = DNFAPI.getItemMythicInfo(itemDetailInfo['mythologyInfo']['options'])
    except:
        hasItemMythicInfo = False

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
        await ctx.message.delete()
        await ctx.channel.send('> !세트 <세트옵션이름> 의 형태로 적어야해요!')
        return

    try:
        setItemIdList = DNFAPI.getSetItemIdList(setItemName)
        setItemId, setItemName = await Util.getSelectionFromSetItemIdList(bot, ctx, setItemIdList)
    except:
        return

    setItemInfoList, setItemOptionList = DNFAPI.getSetItemInfoList(setItemId)
    embed = discord.Embed(title=setItemName + '의 정보를 알려드릴게요.')
    for i in setItemInfoList:
        embed.add_field(name='> ' + i['itemRarity'] + ' ' + i['slotName'], value=i['itemName'] + '\r\n')
    for i in setItemOptionList:
        embed.add_field(name='> ' + str(i['optionNo']) + '세트 옵션', value=i['explain'])
    itemImageUrl = DNFAPI.getItemImageUrl(setItemInfoList[0]['itemId'])
    embed.set_thumbnail(url=itemImageUrl)

    await ctx.channel.send(embed=embed)

@bot.command()
async def 시세(ctx, *input):
    itemName = ''
    for i in input: itemName += i + ' '
    itemName = itemName.rstrip()

    await ctx.message.delete()
    waiting = await ctx.channel.send('> 아이템 시세 정보를 불러오고 있어요...')

    itemName = DNFAPI.getMostSimilarItemName(itemName)
    inputAuctionPrice = DNFAPI.getItemAuctionPrice(itemName)
    if not inputAuctionPrice:
        await waiting.delete()
        await ctx.channel.send('> 해당 아이템의 판매 정보를 얻어오지 못했어요.')
        return

    # KEY 설정
    year, month, day = datetime.today().year, datetime.today().month, datetime.today().day
    key = str(year) + '년' + str(month) + '월' + str(day) + '일'

    # 카드일 경우
    if '카드' in itemName:
        data, priceAndAmountSum = {}, {}
        itemPriceSum, itemAmountSum = {}, {}

        ### 가격합과 판매량을 계산 ###
        for i in inputAuctionPrice:
            prevPriceSum, prevAmountSum = 0, 0
            try:
                prevPriceSum = itemPriceSum[i['upgrade']]
                prevAmountSum = itemAmountSum[i['upgrade']]
            except: pass
            itemPriceSum.update( {i['upgrade'] : prevPriceSum + i['price']} )
            itemAmountSum.update( {i['upgrade'] : prevAmountSum + i['count']} )
            priceAndAmountSum.update( { i['upgrade'] :
                                           {'가격합' : itemPriceSum[i['upgrade']],
                                            '판매량' : itemAmountSum[i['upgrade']]}
                                       } )
        priceAndAmountSum = dict(sorted(priceAndAmountSum.items(), key=lambda x: x[0]))

        ### 계산한 가격합과 판매량으로 평균가 계산 ###
        for i in priceAndAmountSum.keys():
            data.update( {str(i) :
                              {'평균가' : priceAndAmountSum[i]['가격합'] // priceAndAmountSum[i]['판매량'],
                               '판매량' : priceAndAmountSum[i]['판매량']
                               }})

        ### 최근 평균가 불러오기 ###
        prevPriceAvg = {}
        try:
            _key = list(itemAuctionPrice.data[itemName].keys())[-2]
            prevPriceAvg = itemAuctionPrice.data[itemName][_key]
        except:
            for k in data.keys():
                prevPriceAvg.update( {k : {'평균가' : -1}} )

        ### 출력 ###
        embed = discord.Embed(title="'" + itemName + "' 시세를 알려드릴게요")
        for i in data.keys():
            if prevPriceAvg[i]['평균가'] == -1:
                volatility = '데이터 없음'
            else:
                volatility = (data[i]['평균가'] / prevPriceAvg[i]['평균가'] - 1) * 100
                if volatility > 0:
                    volatility = '▲ ' + str(format(volatility, '.2f')) + '%'
                elif volatility == 0:
                    volatility = '- 0.00%'
                else:
                    volatility = '▼ ' + str(format(volatility, '.2f')) + '%'

            embed.add_field(name='> +' + str(i) + ' 평균 가격', value=format(data[i]['평균가'], ',') + '골드')
            embed.add_field(name='> 최근 판매량', value=format(data[i]['판매량'], ',') + '개')
            embed.add_field(name='> 가격 변동률', value=volatility)
        embed.set_footer(text=inputAuctionPrice[-1]['soldDate'] + '부터 ' + inputAuctionPrice[0]['soldDate'] + '까지 집계된 자료예요.')
        embed.set_thumbnail(url=DNFAPI.getItemImageUrl(inputAuctionPrice[0]['itemId']))

        ### 데이터 저장 ###
        try:
            itemAuctionPrice.data[itemName].update( {key : data} )
        except:
            itemAuctionPrice.data[itemName] = {key : data}
        itemAuctionPrice.update()

    # 그 외
    else:
        itemPriceSum  = 0   # 총 가격
        itemAmountSum = 0  # 총 갯수
        priceAverage  = 0  # 평균 가격

        for i in inputAuctionPrice:
            itemPriceSum  += i['price']
            itemAmountSum += i['count']
        priceAverage = itemPriceSum // itemAmountSum

        # 데이터 저장
        data = {'평균가': priceAverage, '판매량': itemAmountSum}
        try:
            itemAuctionPrice.data[itemName].update( {key : data} )
        except:
            itemAuctionPrice.data[itemName] = {key : data}
        itemAuctionPrice.update()

        # 가격 변동률 계산
        prevPriceAvg = -1
        try:
            _key = list(itemAuctionPrice.data[itemName].keys())[-2]
            prevPriceAvg = itemAuctionPrice.data[itemName][_key]['평균가']
        except: pass

        if prevPriceAvg == -1:
            volatility = '데이터 없음'
        else:
            volatility = ((priceAverage / prevPriceAvg) - 1) * 100
            if volatility > 0:
                volatility = '▲ ' + str(format(volatility, '.2f')) + '%'
            elif volatility == 0:
                volatility = '- 0.00%'
            else:
                volatility = '▼ ' + str(format(volatility, '.2f')) + '%'

        embed = discord.Embed(title="'" + itemName + "' 시세를 알려드릴게요")
        embed.add_field(name='> 평균 가격', value=format(priceAverage, ',') + '골드')
        embed.add_field(name='> 최근 판매량', value=format(itemAmountSum, ',') + '개')
        embed.add_field(name='> 가격 변동률', value=volatility)
        embed.set_footer(text=inputAuctionPrice[-1]['soldDate'] + '부터 ' + inputAuctionPrice[0]['soldDate'] + '까지 집계된 자료예요.')
        embed.set_thumbnail(url=DNFAPI.getItemImageUrl(inputAuctionPrice[0]['itemId']))

    await waiting.delete()
    await ctx.channel.send(embed=embed)

@bot.command()
async def 획득에픽(ctx, name='None', _server='전체'):
    if name == 'None':
        await ctx.message.delete()
        await ctx.channel.send('> !획득에픽 <닉네임> 의 형태로 적어야해요!')
        return

    # 검색
    try:
        chrIdList = DNFAPI.getChrIdList(_server, name)
        server, chrId, name = await Util.getSelectionFromChrIdList(bot, ctx, chrIdList)
    except:
        return False

    waiting = await ctx.channel.send('> ' + name + '님의 획득한 에픽을 확인 중이예요...')
    chrTimeLineData = DNFAPI.getChrTimeLine(server, chrId, '505')
    await waiting.delete()

    if len(chrTimeLineData) == 0:
        await ctx.channel.send('> ' + name + '님은 이번 달 획득한 에픽이 없어요.. ㅠㅠ')
        return

    # 결과 출력
    # 15개씩 나눠서 출력
    index = 0
    while index < len(chrTimeLineData):
        start = index
        end = min(start + 15, len(chrTimeLineData))

        if start == 0:
            embed = discord.Embed(title=name + '님이 이번 달에 획득한 에픽을 알려드릴게요!',
                                  description='총 ' + str(len(chrTimeLineData)) + '개의 에픽을 획득하셨네요!')
        else:
            embed = discord.Embed(title=str(start + 1) + ' ~ ' + str(end) + '번째 획득한 에픽들')

        for i in chrTimeLineData[start:end]:
            embed.add_field(
                name='> ' + i['date'][:10] + '\r\n> ch' + str(i['Data']['channelNo']) + '.' + i['Data']['channelName'],
                value=i['Data']['itemName'])
        await ctx.channel.send(embed=embed)

        index += 15

    # 데이터 저장
    today = datetime.today()
    epicRank.add(chrId, {
        'year'  : today.year,
        'month' : today.month,
        'server': server,
        'name'  : name,
        'score' : len(chrTimeLineData)
    })

# @bot.command()
# async def 상세정보(ctx, name='None', _server='전체'):
#     if name == 'None':
#         await ctx.message.delete()
#         await ctx.channel.send('> !상세정보 <닉네임> 의 형태로 적어야해요!')
#         return
#
#     # 검색
#     try:
#         chrIdList = DNFAPI.getChrIdList(_server, name)
#         server, chrId, name = await Util.getSelectionFromChrIdList(bot, ctx, chrIdList)
#     except:
#         return False
#
#     waiting = await ctx.channel.send('> ' + name + '님의 상세정보를 계산 중이예요...')
#
#     ### 정규식 설정 ###
#     rDmgInc       = re.compile('공격시데미지(?P<value>\d+)%증가')
#     rCriDmgInc    = re.compile('크리티컬공격시데미지(?P<value>\d+)%증가')
#     rCriDmgInc2   = re.compile('크리티컬데미지(?P<value>\d+)%증가')
#     rAddDmgInc    = re.compile('공격시데미지증가\S(?P<value>\d+)%추가증가')
#     rAddCriDmgInc = re.compile('크리티컬공격시데미지증가\S(?P<value>\d+)%추가증가')
#     rAddDmg       = re.compile('공격시(?P<value>\d+)%추가데미지')
#     rEleAddDmg    = re.compile('공격시(?P<value>\d+)%속성추가데미지')
#     rAllDmgInc    = re.compile('모든공격력(?P<value>\d+)%증가')
#     rSkillDmgInc  = re.compile('스킬공격력(?P<value>\d+)%증가')
#     rAdApInInc    = re.compile('물리,마법,독립공격력(?P<value>\d+)%')
#     rStrIntInc    = re.compile('힘,지능(?P<value>\d+)%증가')
#     rContinueDmg  = re.compile('적에게입힌피해의(?P<value>\d+)%만큼')
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
#     strIntInc    = 0 # 힘, 지능 증가
#     continueDmg  = 0 # 지속피해
#
#     indiElement  = {'화' : 0, '수' : 0, '명' : 0, '암' : 0}
#     element      = 0 # 모든 속성 강화
#     elementResist= 0 # 암속성 저항
#     ### 선언 끝 ###
#
#     # 장착하고있는 장비템 정보
#     chrEquipItemInfoList, chrEquipSetItemInfo = DNFAPI.getChrEquipItemInfoList(server, chrId)
#     for i in chrEquipItemInfoList:
#         if i['slotName'] == '보조무기':
#             chrEquipItemInfoList.remove(i)
#
#     itemIdList = [i['itemId'] for i in chrEquipItemInfoList]
#     itemNameList = [i['itemName'] for i in chrEquipItemInfoList]
#     setItemIdList = [i['setItemId'] for i in chrEquipSetItemInfo]
#
#     # 크리쳐 추가
#     chrEquipCreatureId = DNFAPI.getChrEquipCreatureId(server, chrId)
#     if chrEquipCreatureId is not None: itemIdList.append(chrEquipCreatureId)
#
#     ### 속성 강화, 저항 ###
#     chrStatInfo = DNFAPI.getChrStatInfo(server, chrId)
#     r = re.compile('(?P<key>\S)속성 강화')
#     for i in chrStatInfo:
#         if i['name'] == '암속성 저항':
#             elementResist = i['value']
#
#         result = r.search(i['name'])
#         if result is not None:
#             indiElement[result.group('key')] = i['value']
#
#     # 이 변수에 옵션들을 저장해서 계산함
#     info = []
#
#     ### 아이템 옵션 계산 ###
#     itemsInfo = DNFAPI.getItemDetails(itemIdList)
#     for i in itemsInfo:
#         iteminfo    = i['itemExplainDetail']
#         itemName    = i['itemName']
#         setItemName = i['setItemName']
#
#         # 태극천제검 :: 음의 기운 기준
#         if itemName == '태극천제검':
#             info.append('스킬 공격력 30% 증가')
#             info.append('물리, 마법, 독립 공격력 40% 증가')
#             info.append('힘, 지능 10% 증가')
#             info.append('모든 공격력 21% 증가')
#             continue
#
#         # 판데모니엄 플레임 :: 스킬 공격력 36% 증가
#         if itemName == '판데모니엄 플레임':
#             info.append('스킬 공격력 36% 증가')
#
#         # 별의 바다 : 바드나후 :: 속추뎀 20퍼로 환산
#         if itemName == '별의 바다 : 바드나후':
#             info.append('공격 시 20% 속성 추가 데미지')
#
#         # 순백의 기도 :: 속성 강화 버프, 물마독 증가
#         if itemName == '순백의 기도':
#             element += 26
#             info.append('물리, 마법, 독립 공격력 15% 증가')
#
#         # 임의 선택 :: 스킬 공격력 5% 로 적용
#         if itemName == '임의 선택':
#             info.append('스킬 공격력 5% 증가')
#             continue
#
#         # 합리적 선택 :: 물마독 20%만 적용
#         if itemName == '합리적 선택':
#             info.append('물리, 마법, 독립 공격력 20% 증가')
#             continue
#
#         # 탈리스만 선택 :: 추뎀 17%만 적용
#         if itemName == '탈리스만 선택':
#             info.append('공격 시 17% 추가 데미지')
#             continue
#
#         # 베테랑 세트 :: 숙련 등급 전설 기준
#         if itemName == '전장의 매':
#             info.append('물리, 마법, 독립 공격력 34% 증가')
#             continue
#
#         if itemName == '퀘이크 프론':
#             info.append('스킬 공격력 34% 증가')
#             continue
#
#         if itemName == '오퍼레이션 델타':
#             element += 68
#             continue
#
#         if itemName == '데파르망':
#             info.append('크리티컬 공격 시 데미지 증가량 34% 추가 증가')
#             continue
#
#         if itemName == '전쟁의 시작':
#             info.append('힘, 지능 34% 증가')
#             continue
#
#         # 싱크로 귀걸이 :: 속성 강화 버프
#         if itemName in ['전자기 진공관', '플라즈마 초 진공관']:
#             element += 40
#
#         # 대자연
#         if  itemName == '포용의 굳건한 대지' or \
#             itemName == '원시 태동의 대지':
#             element += 24
#
#         if itemName == '맹렬히 타오르는 화염':
#             indiElement['화'] = indiElement['화'] + 24
#
#         if itemName == '잠식된 신록의 숨결':
#             indiElement['암'] = indiElement['암'] + 24
#
#         if itemName == '잔잔한 청록의 물결':
#             indiElement['수'] = indiElement['수'] + 24
#
#         if itemName == '휘감는 햇살의 바람':
#             indiElement['명'] = indiElement['명'] + 24
#
#         # 마법사 [???]의 하의 :: 속성 강화, 물마독 증가
#         if itemName == '마법사 [???]의 하의':
#             element += 18
#             elementResist += 18
#             info.append('물리, 마법, 독립 공격력 10% 증가')
#
#         # 종말의 역전 :: 비통한 자의 목걸이, 비운의 유물 착용 시 물마독 10% 감소
#         if itemName == '종말의 역전':
#             if '비통한 자의 목걸이' in itemNameList: adApInInc -= 10
#             if '비운의 유물' in itemNameList: adApInInc -= 10
#
#         # 군신의 숨겨진 유산 세트 :: 2세트 옵션의 크리티컬 데미지 추가 증가를 여기서 계산
#         if  itemName == '군신의 유언장' and \
#             ('군신의 수상한 귀걸이' in itemNameList or '군신의 마지막 갈망' in itemNameList):
#             info.append('크리티컬 공격 시 데미지 증가량 5% 추가 증가')
#
#         # 심연에 빠진 검은 셔츠 :: 속성 저항에 따라 설정
#         if itemName in ['심연에 빠진 검은 셔츠', '고대 심연의 로브']:
#             count = min(elementResist / 10, 5)
#             info.append('모든 공격력 ' + str(7 * count) + '% 증가')
#             continue
#
#         # 타락한 세계수의 생명 :: 속성 저항에 따라 설정
#         if itemName == '타락한 세계수의 생명':
#             count = min(elementResist / 13, 4)
#             info.append('힘, 지능 ' + str(10 * count) + '% 증가')
#             continue
#
#         # 암흑술사가 직접 저술한 고서 :: 속성 저항에 따라 설정
#         if itemName == '암흑술사가 직접 저술한 고서':
#             count = min(elementResist / 7, 7)
#             info.append('물리, 마법, 독립 공격력 ' + str(6 * count) + '% 증가')
#             continue
#
#         # 어둠을 파헤치는 바지 :: 속성 저항에 따라 설정
#         if itemName == '어둠을 파헤치는 바지':
#             count = min(elementResist / 14, 5)
#             info.append('공격 시 데미지 증가량 ' + str(7 * count) + '% 추가 증가')
#             continue
#
#         # 지독한 집념의 탐구 :: 속성 저항에 따라 설정
#         if itemName in ['지독한 집념의 탐구', '영원히 끝나지 않는 탐구']:
#             count = min(elementResist / 18, 4)
#             info.append('모든 공격력 ' + str(7 * count) + '% 증가')
#             element += 10 * count
#             continue
#
#         # 암흑술사의 정수 :: 속성 저항에 따라 설정
#         if itemName == '암흑술사의 정수':
#             count = min(elementResist / 10, 7)
#             info.append('크리티컬 공격 시 데미지 증가량 ' + str(5 * count) + '% 추가 증가')
#             info.append('스킬 공격력 ' + str(count) + '% 증가')
#             continue
#
#         # 나락으로 빠진 발 :: 속성 저항에 따라 설정
#         if itemName == '나락으로 빠진 발':
#             count = min(elementResist / 3, 5)
#             element += 14 * count
#             continue
#
#         # 어둠을 지배하는 고리 :: 속성 저항에 따라 설정
#         if itemName == '어둠을 지배하는 고리':
#             count = min(elementResist / 4, 4)
#             info.append('크리티컬 공격 시 데미지 증가량 ' + str(10 * count) + '% 추가 증가')
#             continue
#
#         # 끝없는 나락의 다크버스 :: 속성 저항에 따라 설정
#         if itemName in ['끝없는 나락의 다크버스', '영원한 나락의 다크버스']:
#             count = min(elementResist / 3, 6)
#             info.append('모든 공격력 ' + str(7 * count) + '% 증가')
#             continue
#
#         # 먼동 세트 :: 따로 계산
#         if setItemName == '먼동 틀 무렵 세트':
#             continue
#
#         # 영보 :: 버프
#         if setItemName == '영보 : 세상의 진리 세트':
#             element += 40
#
#         # 사막 :: 퀵슬롯 6개 비운것을 기준
#         if setItemName == '메마른 사막의 유산 세트':
#             info.append('공격 시 데미지 증가량 5% 추가 증가')
#
#         # 나머지
#         options = iteminfo.split('\n')
#         for i in options:
#             # 예외처리 :: 특정 스킬 데미지 증가
#             exception = re.compile('\d+ 레벨 액티브 스킬 공격력 \d+% 증가')
#             if exception.search(i) is not None: continue
#
#             info.append(i)
#
#     ### 먼동 :: 강화 수치에 따라 옵션 설정
#     for i in chrEquipItemInfoList:
#         itemName = i['itemName']
#         if itemName == '새벽을 녹이는 따스함':
#             info.append('모든 공격력 6% 증가')
#             info.append('스킬 공격력 ' + str(4 + i['reinforce']) + '% 증가')
#
#         elif itemName == '달빛을 가두는 여명':
#             info.append('물리, 마법, 독립 공격력 6% 증가')
#             info.append('힘, 지능 ' + str(4 + i['reinforce']) + '% 증가')
#
#         elif itemName == '새벽을 감싸는 따스함':
#             info.append('모든 공격력 6% 증가')
#             info.append('스킬 공격력 ' + str(4 + i['reinforce']) + '% 증가')
#
#         elif itemName == '고요를 머금은 이슬':
#             info.append('공격 시 데미지 증가량 ' + str(4 + i['reinforce']) + '% 추가 증가')
#
#     ### 신화 옵션 계산 ###
#     for i in chrEquipItemInfoList:
#         try:
#             for j in i['mythologyInfo']['options']:
#                 info.append(j['explain'])
#         except: pass
#
#     ### 시로코 옵션 계산 ###
#     chrSirocoItemInfo = Util.getSirocoItemInfo(chrEquipItemInfoList)
#     if chrSirocoItemInfo is not None:
#         # 1세트 옵션
#         for k in chrSirocoItemInfo.keys():
#             try:
#                 info.append(chrSirocoItemInfo[k]['1옵션'])
#             except: pass
#
#         # 2세트 옵션
#         # 잔향
#         if 3 in chrSirocoItemInfo['세트'].values():
#             try:
#                 info.append(chrSirocoItemInfo['잔향']['2옵션'])
#             except: pass
#
#         # 넥스
#         if  '무형 : 넥스의 잠식된 의복' in chrSirocoItemInfo.keys() and \
#             '무의식 : 넥스의 몽환의 어둠' in chrSirocoItemInfo.keys():
#             info.append(chrSirocoItemInfo['무형 : 넥스의 잠식된 의복']['2옵션'])
#         if '무의식 : 넥스의 몽환의 어둠' in chrSirocoItemInfo.keys() and \
#             '환영 : 넥스의 검은 기운' in chrSirocoItemInfo.keys():
#             info.append(chrSirocoItemInfo['무의식 : 넥스의 몽환의 어둠']['2옵션'])
#         if '환영 : 넥스의 검은 기운' in chrSirocoItemInfo.keys() and \
#             '무형 : 넥스의 잠식된 의복' in chrSirocoItemInfo.keys():
#             info.append(chrSirocoItemInfo['환영 : 넥스의 검은 기운']['2옵션'])
#
#         # 암살자
#         if  '무형 : 암살자의 잠식된 의식' in chrSirocoItemInfo.keys() and \
#             '무의식 : 암살자의 몽환의 흔적' in chrSirocoItemInfo.keys():
#             info.append(chrSirocoItemInfo['무형 : 암살자의 잠식된 의식']['2옵션'])
#
#         if '무의식 : 암살자의 몽환의 흔적' in chrSirocoItemInfo.keys() and \
#             '환영 : 암살자의 검은 검집' in chrSirocoItemInfo.keys():
#             info.append(chrSirocoItemInfo['무의식 : 암살자의 몽환의 흔적']['2옵션'])
#
#         if '환영 : 암살자의 검은 검집' in chrSirocoItemInfo.keys() and \
#             '무형 : 암살자의 잠식된 의식' in chrSirocoItemInfo.keys():
#             info.append(chrSirocoItemInfo['환영 : 암살자의 검은 검집']['2옵션'])
#
#         # 수문장
#         if  '무형 : 수문장의 잠식된 갑주' in chrSirocoItemInfo.keys() and \
#             '무의식 : 수문장의 몽환의 사념' in chrSirocoItemInfo.keys():
#             element += 30
#         if  '무의식 : 수문장의 몽환의 사념' in chrSirocoItemInfo.keys() and \
#             '환영 : 수문장의 검은 가면' in chrSirocoItemInfo.keys():
#             element += 30
#         if  '환영 : 수문장의 검은 가면' in chrSirocoItemInfo.keys() and \
#             '무형 : 수문장의 잠식된 갑주' in chrSirocoItemInfo.keys():
#             element += 30
#
#         # 로도스
#         if  '무형 : 로도스의 잠식된 의지' in chrSirocoItemInfo.keys() and \
#             '무의식 : 로도스의 몽환의 근원' in chrSirocoItemInfo.keys():
#             info.append(chrSirocoItemInfo.get('무형 : 로도스의 잠식된 의지')['2옵션'])
#         if '무의식 : 로도스의 몽환의 근원' in chrSirocoItemInfo.keys() and \
#             '환영 : 로도스의 검은 핵' in chrSirocoItemInfo.keys():
#             info.append(chrSirocoItemInfo.get('무의식 : 로도스의 몽환의 근원')['2옵션'])
#         if '환영 : 로도스의 검은 핵' in chrSirocoItemInfo.keys() and \
#             '무형 : 로도스의 잠식된 의지' in chrSirocoItemInfo.keys():
#             info.append(chrSirocoItemInfo.get('환영 : 로도스의 검은 핵')['2옵션'])
#
#     ### 세트 옵션 계산 ###
#     setItemInfos = DNFAPI.getSetItemInfos(setItemIdList)
#
#     for i in setItemInfos:
#         for j in chrEquipSetItemInfo:
#             if i['setItemName'] == j['setItemName']:
#                 i.update({'activeSetNo' : j['activeSetNo']})
#
#     for i in setItemInfos:
#         for j in i['setItemOption']:
#             if i['activeSetNo'] >= j['optionNo']:
#                 setItemName = i['setItemName']
#
#                 # 행운의 트라이앵글 3세트 :: 77 기준
#                 if setItemName == '행운의 트라이앵글 세트' and j['optionNo'] == 3:
#                     info.append('스킬 공격력 31% 증가')
#                     continue
#
#                 # 운명의 주사위 3세트 :: 6 기준
#                 if setItemName == '운명의 주사위 세트' and j['optionNo'] == 3:
#                     info.append('힘, 지능 14% 증가')
#                     continue
#
#                 # 메마른 사막의 유산 2세트 :: 퀵슬롯 6개 비운것 기준
#                 if setItemName == '메마른 사막의 유산 세트' and j['optionNo'] == 2:
#                     info.append('물리, 마법, 독립 공격력 22% 증가')
#                     info.append('스킬 공격력 6% 증가')
#                     continue
#
#                 # 베테랑 군인의 정복 5세트 :: 숙련 등급 전설 기준
#                 if setItemName == '베테랑 군인의 정복 세트' and j['optionNo'] == 5:
#                     info.append('공격 시 40% 추가 데미지')
#                     continue
#
#                 # 흑마술의 탐구자 세트 :: 암속성 저항에 따라 설정
#                 if setItemName == '흑마술의 탐구자 세트':
#                     if j['optionNo'] == 2 and elementResist >= 76:
#                         info.append('공격 시 데미지 증가량 12% 추가 증가')
#                         info.append('스킬 공격력 10% 증가')
#                         continue
#                     if j['optionNo'] == 3 and elementResist >= 81:
#                         info.append('공격 시 13% 속성 추가 데미지')
#                         continue
#
#                 # 나락의 구도자 세트 :: 암속성 저항에 따라 설정
#                 if setItemName == '나락의 구도자 세트':
#                     if j['optionNo'] == 2 and elementResist >= 21:
#                         info.append('모든 공격력 10% 증가')
#                         info.append('공격 시 10% 추가 데미지')
#                         continue
#                     if j['optionNo'] == 3:
#                         count = min(elementResist / 7, 4)
#                         info.append('스킬 공격력 ' + str(4 * count) + '% 증가')
#                         element += 10 * count
#                         continue
#
#                 # 군신의 숨겨진 유산
#                 if setItemName == '군신의 숨겨진 유산 세트':
#                     # 크리티컬 추가 데미지는 이미 계산함
#                     if j['optionNo'] == 2:
#                         info.append('물리, 마법, 독립 공격력 10% 증가')
#                         info.append('모든 공격력 8% 증가')
#                         continue
#                     # 이동속도 최대 기준
#                     if j['optionNo'] == 3:
#                         info.append('스킬 공격력 10% 증가')
#                         info.append('힘, 지능 10% 증가')
#                         continue
#
#                 # 나머지
#                 try:
#                     option = j['explain'].replace('\r', '')
#                     option = option.split('\n')
#                     info += option
#                 except: pass
#
#     ### 계산 ###
#     for i in info:
#         i = i.replace(' ', '')
#
#         # 데미지, 크리티컬 데미지 증가
#         tCriDmgInc = rCriDmgInc.search(i)
#         tCriDmgInc2 = rCriDmgInc2.search(i)
#         if tCriDmgInc is not None and criDmgInc < int(tCriDmgInc.group('value')):
#             criDmgInc = int(tCriDmgInc.group('value'))
#         elif tCriDmgInc2 is not None and criDmgInc < int(tCriDmgInc2.group('value')):
#             criDmgInc = int(tCriDmgInc2.group('value'))
#         else:
#             tDmgInc = rDmgInc.search(i)
#             if tDmgInc is not None and dmgInc < int(tDmgInc.group('value')):
#                 dmgInc = int(tDmgInc.group('value'))
#
#         # 데미지, 크리티컬 데미지 추가 증가
#         tAddCriDmgInc = rAddCriDmgInc.search(i)
#         if tAddCriDmgInc is not None:
#             addCriDmgInc += int(tAddCriDmgInc.group('value'))
#         else:
#             tAddDmgInc = rAddDmgInc.search(i)
#             if tAddDmgInc is not None:
#                 addDmgInc += int(tAddDmgInc.group('value'))
#
#         # 추가 데미지
#         tAddDmg = rAddDmg.search(i)
#         if tAddDmg is not None:
#             addDmg += int(tAddDmg.group('value'))
#
#         # 속성 추가 데미지
#         tEleDmg = rEleAddDmg.search(i)
#         if tEleDmg is not None:
#             eleAddDmg += int(tEleDmg.group('value'))
#
#         # 모든 공격력 증가
#         tAllDmgInc = rAllDmgInc.search(i)
#         if tAllDmgInc is not None:
#             allDmgInc += int(tAllDmgInc.group('value'))
#
#         # 스킬 데미지 증가
#         tSkillDmgInc = rSkillDmgInc.search(i)
#         if tSkillDmgInc is not None:
#             skillDmgInc *= 1 + float(tSkillDmgInc.group('value')) / 100
#
#         # 물마독 증가
#         tAdAPInInc = rAdApInInc.search(i)
#         if tAdAPInInc is not None:
#             adApInInc += int(tAdAPInInc.group('value'))
#
#         # 힘지능 증가
#         tStrIntInc = rStrIntInc.search(i)
#         if tStrIntInc is not None:
#             strIntInc += int(tStrIntInc.group('value'))
#
#         # 지속 피해
#         tContinueDmg = rContinueDmg.search(i)
#         if tContinueDmg is not None:
#             continueDmg += int(tContinueDmg.group('value'))
#
#     # 모든 속성 강화 += 속성 강화 중 가장 큰 값
#     element += max(indiElement.values())
#
#     # 속추뎀 -> 추뎀 변환
#     eleAddDmg = int(eleAddDmg * (1.05 + 0.0045 * element))
#
#     # 스증뎀 변환
#     skillDmgInc = round((skillDmgInc - 1) * 100)
#     if skillDmgInc == 1:
#         skillDmgInc = 0
#
#     # 데미지 계산
#     damage = Util.getFinalDamage(dmgInc, addDmgInc, criDmgInc, addCriDmgInc, addDmgInc, eleAddDmg, allDmgInc, adApInInc, strIntInc, element, skillDmgInc, continueDmg)
#
#     # 랭킹 추가
#     setRank.add(chrId, {
#                         'server' : server,
#                         'name' : name,
#                         'score' : damage
#                         })
#     await waiting.delete()
#
#     embed = discord.Embed(title=name + '님의 상세정보를 알려드릴게요.')
#     embed.add_field(name='> 데미지 증가',              value=str(dmgInc + addDmgInc) + '%')
#     embed.add_field(name='> 크리티컬 데미지 증가',     value=str(criDmgInc + addCriDmgInc) + '%')
#     embed.add_field(name='> 추가 데미지',              value=str(addDmg + eleAddDmg) + '% (' + str(addDmg) + '% + ' + str(eleAddDmg) + '%)')
#     embed.add_field(name='> 모든 공격력 증가',         value=str(allDmgInc) + '%')
#     embed.add_field(name='> 스킬 데미지 증가',         value=str(skillDmgInc) + '%')
#     embed.add_field(name='> 물리마법독립 공격력 증가', value=str(adApInInc) + '%')
#     embed.add_field(name='> 힘, 지능 증가',            value=str(strIntInc) + '%')
#     embed.add_field(name='> 지속 피해',                value=str(continueDmg) + '%')
#     embed.add_field(name='> 세팅 점수',                value=str(damage) + '점')
#     embed.set_footer(text='세팅 점수는 데미지 증가 옵션만을 고려해서 나온 점수예요.')
#     await ctx.channel.send(embed=embed)
#
#     # 데미지 효율 계산
#     embed2 = discord.Embed(title='각 능력치 별 효율도 알려드릴게요.')
#
#     dmgInc10 = Util.getFinalDamage(dmgInc, addDmgInc + 10, criDmgInc, addCriDmgInc, addDmgInc, eleAddDmg, allDmgInc, adApInInc, strIntInc, element, skillDmgInc, continueDmg)
#     embed2.add_field(name='> 데미지 10%', value='스킬 데미지 ' + str(round((dmgInc10 / damage - 1) * 1000) / 10) + '%')
#
#     criDmgInc10 = Util.getFinalDamage(dmgInc, addDmgInc, criDmgInc, addCriDmgInc + 10, addDmgInc, eleAddDmg, allDmgInc, adApInInc, strIntInc, element, skillDmgInc, continueDmg)
#     embed2.add_field(name='> 크리티컬 데미지 10%', value='스킬 데미지 ' + str(round((criDmgInc10 / damage - 1) * 1000) / 10) + '%')
#
#     addDmgInc10 = Util.getFinalDamage(dmgInc, addDmgInc, criDmgInc, addCriDmgInc, addDmgInc + 10, eleAddDmg, allDmgInc, adApInInc, strIntInc, element, skillDmgInc, continueDmg)
#     embed2.add_field(name='> 추가 데미지 10%', value='스킬 데미지 ' + str(round((addDmgInc10 / damage - 1) * 1000) / 10) + '%')
#
#     allDmgInc10 = Util.getFinalDamage(dmgInc, addDmgInc, criDmgInc, addCriDmgInc, addDmgInc, eleAddDmg, allDmgInc + 10, adApInInc, strIntInc, element, skillDmgInc, continueDmg)
#     embed2.add_field(name='> 모든 공격력 10%', value='스킬 데미지 ' + str(round((allDmgInc10 / damage - 1) * 1000) / 10) + '%')
#
#     adApInInc10 = Util.getFinalDamage(dmgInc, addDmgInc, criDmgInc, addCriDmgInc, addDmgInc, eleAddDmg, allDmgInc, adApInInc + 10, strIntInc, element, skillDmgInc, continueDmg)
#     embed2.add_field(name='> 물리마법독립 10%', value='스킬 데미지 ' + str(round((adApInInc10 / damage - 1) * 1000) / 10) + '%')
#
#     strIntInc10 = Util.getFinalDamage(dmgInc, addDmgInc, criDmgInc, addCriDmgInc, addDmgInc, eleAddDmg, allDmgInc, adApInInc, strIntInc + 10, element, skillDmgInc, continueDmg)
#     embed2.add_field(name='> 힘, 지능 10%', value='스킬 데미지 ' + str(round((strIntInc10 / damage - 1) * 1000) / 10) + '%')
#
#     continueDmgInc10 = Util.getFinalDamage(dmgInc, addDmgInc, criDmgInc, addCriDmgInc, addDmgInc, eleAddDmg, allDmgInc, adApInInc, strIntInc, element, skillDmgInc, continueDmg + 10)
#     embed2.add_field(name='> 지속 데미지 10%', value='스킬 데미지 ' + str(round((continueDmgInc10 / damage - 1) * 1000) / 10) + '%')
#     embed2.set_footer(text='이 수치들은 참고만 해주세요! 오차가 있을 수 있어요.')
#     await ctx.channel.send(embed=embed2)

@bot.command()
async def 기린랭킹(ctx):
    today = datetime.today()
    epicRank.update(today.month)
    embed = discord.Embed(title=str(today.year) + '년 ' + str(today.month) + '월 기린 랭킹을 알려드릴게요!', description='랭킹은 매달 초기화되며 15등까지만 보여드려요.')
    embed.set_footer(text='모두 원하는 에픽/신화를 얻을 수 있으면 좋겠어요!')

    rank = 1
    for k in epicRank.data.keys():
        name  = '> ' + str(rank) + '등\r\n> ' + epicRank.data[k]['server'] + ' ' + epicRank.data[k]['name']
        value = '에픽 ' + str(epicRank.data[k]['score']) + '개 획득!'
        embed.add_field(name=name, value=value)
        rank += 1

    if rank == 1:
        embed.add_field(name='> 랭킹에 아무도 없어요!', value='> !획득에픽 <닉네임> 으로 자신의 캐릭터를 랭킹에 추가해보세요!')
    await ctx.message.delete()
    await ctx.channel.send(embed=embed)

# @bot.command()
# async def 세팅랭킹(ctx):
#     embed = discord.Embed(title='세팅 랭킹을 알려드릴게요!', description='랭킹은 15등까지만 보여드려요.')
#     embed.set_footer(text='더 이상 업데이트 때문에 랭킹이 초기화되지 않아요!')
#
#     rank = 1
#     for k in setRank.data.keys():
#         embed.add_field(name='> ' + str(rank) + '등\r\n> ' + setRank.data[k]['server'] + ' ' + setRank.data[k]['name'], value=str(setRank.data[k]['score']) + '점')
#         rank += 1
#
#     if rank == 1:
#         embed.add_field(name='> 랭킹에 아무도 없어요!', value='> !상세정보 <닉네임> 으로 자신의 캐릭터를 랭킹에 추가해보세요!')
#
#     await ctx.message.delete()
#     await ctx.channel.send(embed=embed)

@bot.command()
async def 청소(ctx):
    await ctx.message.delete()
    def check(m): return m.author == bot.user
    await ctx.channel.purge(check=check)

### 제작자 명령어 ###
@bot.command()
async def 상태(ctx, *state):
    if ctx.message.author.id == ownerId:
        _state = ''
        for i in state:
            _state += i + ' '
        _state = _state.rstrip()

        await bot.change_presence(status=discord.Status.online, activity=discord.Game(_state))
        await ctx.message.delete()
        await ctx.channel.send("> '" + _state + "하는 중' 으로 상태를 바꿨습니다.")

@bot.command()
async def 연결(ctx):
    if ctx.message.author.id == ownerId:
        await ctx.message.delete()
        await ctx.channel.send('> 시크봇은 ' + str(len(bot.guilds)) + '개의 서버에 연결되어있어요!')

@bot.command()
async def 통계(ctx):
    if ctx.message.author.id == ownerId:
        await ctx.message.delete()
        embed = discord.Embed(title='유저들이 사용한 각 명령어의 사용 횟수를 알려드릴게요.')
        for k in cmdStatistics.data.keys():
            embed.add_field(name='> ' + k, value=str(cmdStatistics.data[k]) + '번')
        await ctx.channel.send(embed=embed)

bot.remove_command('help')
bot.run(token)
