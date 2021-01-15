import discord
from SRC import Util
from FrameWork import DNFAPI

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

async def 캐릭터(bot, ctx, name='None', server='전체'):
    if name == 'None':
        await ctx.message.delete()
        await ctx.channel.send('> !캐릭터 <닉네임> 의 형태로 적어야해요!')
        return

    # 검색
    try:
        chrIdList = DNFAPI.getChrIdList(server, name)
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

async def 시세(ctx, itemAuctionPrice, *input):
    await ctx.message.delete()
    waiting = await ctx.channel.send('> 아이템 시세 정보를 불러오고 있어요...')

    itemName = Util.mergeString(*input)
    itemName = DNFAPI.getMostSimilarItemName(itemName)
    inputAuctionPrice = DNFAPI.getItemAuctionPrice(itemName)
    if not inputAuctionPrice:
        await waiting.delete()
        await ctx.channel.send('> 해당 아이템의 판매 정보를 얻어오지 못했어요.')
        return

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
                volatility = float(format(volatility, '.2f'))
                if volatility > 0:
                    volatility = '▲ ' + str(volatility) + '%'
                elif volatility == 0:
                    volatility = '- 0.00%'
                else:
                    volatility = '▼ ' + str(volatility) + '%'
            embed.add_field(name='> +' + str(i) + ' 평균 가격', value=format(data[i]['평균가'], ',') + '골드')
            embed.add_field(name='> 최근 판매량', value=format(data[i]['판매량'], ',') + '개')
            embed.add_field(name='> 가격 변동률', value=volatility)
        embed.set_footer(text=inputAuctionPrice[-1]['soldDate'] + '부터 ' + inputAuctionPrice[0]['soldDate'] + '까지 집계된 자료예요.')
        embed.set_thumbnail(url=DNFAPI.getItemImageUrl(inputAuctionPrice[0]['itemId']))

    # 그 외
    else:
        itemPriceSum  = 0   # 총 가격
        itemAmountSum = 0  # 총 갯수
        priceAverage  = 0  # 평균 가격

        for i in inputAuctionPrice:
            itemPriceSum  += i['price']
            itemAmountSum += i['count']
        priceAverage = itemPriceSum // itemAmountSum
        data = {'평균가': priceAverage, '판매량': itemAmountSum}

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

    ### 데이터 저장 ###
    try:
        itemAuctionPrice.data[itemName].update( {Util.getToday() : data} )
    except:
        itemAuctionPrice.data[itemName] = {Util.getToday() : data}
    itemAuctionPrice.update()

    await waiting.delete()
    await ctx.channel.send(embed=embed)

async def 장비(bot, ctx, *input):
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

async def 세트(bot, ctx, *input):
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