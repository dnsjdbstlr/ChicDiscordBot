import discord
from SRC import Util
from FrameWork import DNFAPI
import re

async def 등급(ctx):
    await ctx.message.delete()
    waiting = await ctx.channel.send('> 오늘의 아이템 등급을 읽어오고있어요...')

    itemIdList = ['8e0233bd504efc762b76a476d0e08de4', '52b3fac226cfa92cba9cffff516fb06e',
                  '7fae76b5a3fd513001a5d40716e1287f']

    MAX_OPTION = {
        '8e0233bd504efc762b76a476d0e08de4' : {
            '물리 방어력': 4475,
            '힘': 57,
            '지능': 37,
            '모든 속성 강화': 22
        },
        '52b3fac226cfa92cba9cffff516fb06e' : {
            '물리 방어력': 2983,
            '힘': 47,
            '지능': 47,
            '정신력': 52,
            '모든 속성 강화': 14
        },
        '7fae76b5a3fd513001a5d40716e1287f' : {
            '물리 공격력': 1113,
            '마법 공격력': 1348,
            '독립 공격력': 719,
            '지능': 78
        }
    }

    shopItemInfo = [DNFAPI.getShopItemInfo(i) for i in itemIdList]

    embed = discord.Embed(title='오늘의 아이템 등급을 알려드릴게요!')
    for i in shopItemInfo:
        value = i['itemGradeName'] + '(' + str(i['itemGradeValue']) + '%)\r\n'
        for j in i['itemStatus']:
            if j['name'] in MAX_OPTION[i['itemId']].keys():
                diff = j['value'] - MAX_OPTION[i['itemId']][j['name']]
                value += j['name'] + ' : ' + str(j['value']) + '(' + str(diff) + ')\r\n'
        embed.add_field(name='> ' + i['itemName'], value=value)

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
    else:
        footer = '오류'
    embed.set_footer(text=footer)

    await waiting.delete()
    await ctx.channel.send(embed=embed)

async def 캐릭터(bot, ctx, name='None', server='전체'):
    if name == 'None':
        await ctx.message.delete()
        await ctx.channel.send('> !캐릭터 <닉네임> 의 형태로 적어야해요!')
        return

    try:
        chrIdList = DNFAPI.getChrIdList(server, name)
        server, chrId, name = await Util.getSelectionFromChrIdList(bot, ctx, chrIdList)
    except:
        return False

    chrEquipItemInfo = DNFAPI.getChrEquipItemInfoList(server, chrId)

    ### embed 선언 ###
    embed = discord.Embed(title=name + '님의 캐릭터 정보를 알려드릴게요.')

    ### 장착중인 세트 ###
    equipSetItem = ''
    for i in chrEquipItemInfo['equipment']:
        equipSetItem += i['setItemName'] + '(' + str(i['activeSetNo']) + ')\r\n'
    if equipSetItem != '':
        embed.add_field(name='> 장착중인 세트', value=equipSetItem, inline=False)

    ### 장비 옵션 ###
    for i in chrEquipItemInfo['setItemInfo']:
        if i['slotName'] in ['칭호', '보조무기']: continue

        text = ''

        ### 강화, 재련 수치 ###
        if i['reinforce'] != 0:
            text += '+' + str(i['reinforce'])
        if i['refine'] != 0:
            text += '(' + str(i['refine']) + ')'
        text += ' ' + i['itemName'] + '\r\n'

        ### 마법부여 ###
        try:
            for j in i['enchant']['status']:
                text += j['name'] + ' +' + str(j['value']) + '\r\n'
        except: pass

        embed.add_field(name='> ' + i['slotName'], value=text)
    embed.set_footer(text=name + '님의 캐릭터 이미지도 챙겨왔어요!')
    embed.set_image(url='https://img-api.neople.co.kr/df/servers/' + DNFAPI.SERVER_ID[server] + '/characters/' + chrId + '?zoom=1')
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
        prevPriceAvg, prevPriceDay = {}, ''
        try:
            keys = list(itemAuctionPrice.data[itemName].keys())
            if keys[-1] == Util.getToday():
                key = keys[-2]
            else:
                key = keys[-1]
            prevPriceAvg = itemAuctionPrice.data[itemName][key]
            prevPriceDay = Util.convertDateToHyphen(str(key))
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
                volatility += ' ' + prevPriceDay
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
        prevPriceAvg, prevPriceDay = -1, ''
        try:
            keys = list(itemAuctionPrice.data[itemName].keys())
            if keys[-1] == Util.getToday():
                key = keys[-2]
            else:
                key = keys[-1]
            prevPriceAvg = itemAuctionPrice.data[itemName][key]['평균가']
            prevPriceDay = Util.convertDateToHyphen(str(key))
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
            volatility += ' ' + prevPriceDay

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
    name = Util.mergeString(*input)

    if len(name) < 1:
        await ctx.message.delete()
        await ctx.channel.send('> !장비 <장비템이름> 의 형태로 적어야해요!')
        return

    try:
        itemIdList = DNFAPI.getItemId(name)
        itemId = await Util.getSelectionFromItemIdList(bot, ctx, itemIdList)
        if itemId is False: return
    except: return

    itemDetailInfo = DNFAPI.getItemDetail(itemId)
    itemImageUrl = DNFAPI.getItemImageUrl(itemId)
    embed = discord.Embed(title=itemDetailInfo['itemName'],
                          description=str(itemDetailInfo['itemAvailableLevel']) + 'Lv ' + itemDetailInfo['itemRarity'] + ' ' + itemDetailInfo['itemTypeDetail'])
    # 스탯
    itemStatInfo = DNFAPI.getItemStatInfo(itemDetailInfo['itemStatus'])
    embed.add_field(name='> 스탯', value=itemStatInfo, inline=False)

    # 스킬 레벨
    try:
        itemSkillLvInfo = DNFAPI.getItemSkillLvInfo(itemDetailInfo['itemReinforceSkill'][0]['jobName'],
                                                    itemDetailInfo['itemReinforceSkill'][0]['levelRange'])
        embed.add_field(name='> 스킬', value=itemSkillLvInfo)
    except: pass

    # 기본 옵션
    embed.add_field(name='> 옵션', value=itemDetailInfo['itemExplainDetail'], inline=False)

    # 변환 옵션
    try:
        itemTransformInfo = itemDetailInfo['transformInfo']['explain']
        embed.add_field(name='> 변환 옵션', value=itemTransformInfo, inline=False)
    except: pass

    # 신화옵션
    try:
        itemMythicInfo = DNFAPI.getItemMythicInfo(itemDetailInfo['mythologyInfo']['options'])
        embed.add_field(name='> 신화 전용 옵션', value=itemMythicInfo, inline=False)
    except: pass

    # 플레이버 텍스트
    itemFlavorText = itemDetailInfo['itemFlavorText']

    embed.set_footer(text=itemFlavorText)
    embed.set_thumbnail(url=itemImageUrl)
    msg = await ctx.channel.send(embed=embed)

    ### 버퍼 전용 옵션 ###
    await msg.add_reaction('❤️')
    try:
        def check(reaction, user):
            return str(reaction) == '❤️' and user == ctx.author and reaction.message.id == msg.id
        reaction, user = await bot.wait_for('reaction_add', check=check)
    except: pass
    else:
        await msg.edit(embed=Util.getBuffOptionFromItemDetailInfo(itemDetailInfo))
        await msg.clear_reactions()

async def 세트(bot, ctx, *input):
    name = Util.mergeString(*input)

    if len(name) < 1:
        await ctx.message.delete()
        await ctx.channel.send('> !세트 <세트옵션이름> 의 형태로 적어야해요!')
        return

    try:
        setItemIdList = DNFAPI.getSetItemIdList(name)
        setItemId, name = await Util.getSelectionFromSetItemIdList(bot, ctx, setItemIdList)
    except:
        return

    setItemInfo = DNFAPI.getSetItemInfoList(setItemId)
    embed = discord.Embed(title=name + '의 정보를 알려드릴게요.')
    for setItem in setItemInfo['setItems']:
        embed.add_field(name='> ' + setItem['itemRarity'] + ' ' + setItem['slotName'], value=setItem['itemName'])
    for option in setItemInfo['setItemOption']:
        value = ''
        try:
            for status in option['status']:
                value += status['name'] + ' ' + status['value'] + '\r\n'
        except: pass
        embed.add_field(name='> ' + str(option['optionNo']) + '세트 옵션', value=value + option['explain'])
    embed.set_thumbnail(url=DNFAPI.getItemImageUrl(setItemInfo['setItems'][0]['itemId']))
    msg = await ctx.channel.send(embed=embed)

    ### 버퍼 전용 옵션 ###
    await msg.add_reaction('❤️')
    try:
        def check(reaction, user):
            return str(reaction) == '❤️' and user == ctx.author and reaction.message.id == msg.id
        reaction, user = await bot.wait_for('reaction_add', check=check)
    except: pass
    else:
        await msg.edit(embed=Util.getBuffOptionFromItemSetOption(setItemInfo))
        await msg.clear_reactions()

async def 버프력(bot, ctx, name, server='전체'):
    if name == 'None':
        await ctx.message.delete()
        await ctx.channel.send('> !버프력 <닉네임> 의 형태로 적어야해요!')
        return

    # 검색
    try:
        chrIdList = DNFAPI.getChrIdList(server, name)
        server, chrId, name = await Util.getSelectionFromChrIdList(bot, ctx, chrIdList)
    except: return False

    ### 계산에 필요한 데이터 불러오기 ###
    chrStatInfo     = DNFAPI.getChrStatInfo(server, chrId)
    chrSkillStyle   = DNFAPI.getChrSkillStyle(server, chrId)
    chrEquipData    = DNFAPI.getChrEquipItemInfoList(server, chrId)
    chrAvatarData   = DNFAPI.getChrAvatarData(server, chrId)
    chrBuffEquip    = DNFAPI.getChrBuffEquip(server, chrId)
    allItemOption   = Util.getChrAllItemOptions(chrEquipData, chrAvatarData)

    Util.getApplyStatFromBuffEquip(chrBuffEquip)

    ### 스킬 정보 불러오기 ###
    ACTIVE_BUFF2_INFO = DNFAPI.getSkillInfo('3909d0b188e9c95311399f776e331da5', '56fca6cff74d828e92301a40cd2148b9') # 1각 액티브
    ACTIVE_BUFF3_INFO = DNFAPI.getSkillInfo('3909d0b188e9c95311399f776e331da5', 'caef38e23a8ae551466f8a8eb039df22') # 진각 액티브
    PASSIVE_BUFF_INFO = DNFAPI.getSkillInfo('3909d0b188e9c95311399f776e331da5', '0dbdeaf846356f8b9380f8fbb8e97377') # 1각 패시브

    ### 캐릭터 스킬 레벨 ###
    chrApplyStat    = Util.getChrSpecificStat(chrStatInfo, '지능')
    chr48LvSkillLv  = Util.getChrSkillLv(chrSkillStyle, '0dbdeaf846356f8b9380f8fbb8e97377', False)
    chr50LvSkillLv  = Util.getChrSkillLv(chrSkillStyle, '56fca6cff74d828e92301a40cd2148b9')
    chr100LvSkillLv = Util.getChrSkillLv(chrSkillStyle, 'caef38e23a8ae551466f8a8eb039df22')

    ### 변수 선언 ###
    ACTIVE_BUFF1_SKILL_LV    = 0 # 30레벨 버프 스킬 레벨
    ACTIVE_BUFF2_SKILL_LV    = 0 # 50레벨 버프 스킬 레벨
    ACTIVE_BUFF3_SKILL_LV    = 0 # 100레벨 버프 스킬 레벨
    PASSIVE_BUFF_SKILL_LV    = 0 # 48레벨 패시브 버프 스킬 레벨
    ACTIVE_BUFF1_SKILL_STAT  = 0 # 30레벨 버프 스킬 힘, 지능 퍼센트 증가량
    ACTIVE_BUFF2_SKILL_STAT1 = 0 # 50Lv 액티브 스킬 힘, 지능 증가량
    ACTIVE_BUFF2_SKILL_STAT2 = 0 # 50Lv 액티브 스킬 힘, 지능 퍼센트 증가량

    ForbiddenCurseLv = 0 # 금단의 저주
    MarionetteLv     = 0 # 마리오네트
    smallDevilLv     = 0 # 소악마

    ### 정규식 ###
    ACTIVE_BUFF1_SKILL_LV_RE    = re.compile('30Lv버프스킬레벨\+(?P<value>\d+)')
    ACTIVE_BUFF2_SKILL_LV_RE    = re.compile('50Lv액티브스킬레벨\+(?P<value>\d+)')
    ACTIVE_BUFF2_SKILL_STAT1_RE = re.compile('50Lv액티브스킬힘,지능증가량(?P<value>\d+)증가')
    ACTIVE_BUFF2_SKILL_STAT2_RE = re.compile('50Lv액티브스킬힘,지능증가량(?P<value>\d+)%증가')
    INC_SKILL_LV1_RE            = re.compile('모든직업(?P<value1>\d+)레벨모든스킬Lv\+(?P<value2>\d+)')
    INC_SKILL_LV2_RE            = re.compile('모든직업(?P<value1>\d+)~(?P<value2>\d+)레벨모든스킬Lv\+(?P<value3>\d+)')

    ForbiddenCurse_RE = re.compile('금단의저주스킬Lv\+(?P<value>\d+)')
    MarionetteLv_RE   = re.compile('마리오네트스킬Lv\+(?P<value>\d+)')
    smallDevilLv_RE   = re.compile('소악마스킬Lv\+(?P<value>\d+)')

    ### 계산 ###
    for option in allItemOption:
        try:
            option = option.replace(' ', '')
        except: pass

        try:
            ### 30 레벨 스킬 레벨 증가 ###
            result = ACTIVE_BUFF1_SKILL_LV_RE.search(option)
            ACTIVE_BUFF1_SKILL_LV += int(result.group('value'))
        except: pass

        try:
            ### 50 레벨 스킬 레벨 증가 ###
            result = ACTIVE_BUFF2_SKILL_LV_RE.search(option)
            ACTIVE_BUFF2_SKILL_LV += int(result.group('value'))
        except: pass

        try:
            ### 50 레벨 스킬 힘, 지능 증가량1 ###
            result = ACTIVE_BUFF2_SKILL_STAT1_RE.search(option)
            ACTIVE_BUFF2_SKILL_STAT1 += int(result.group('value'))
        except: pass

        try:
            ### 50 레벨 스킬 힘, 지능 증가량2 ###
            result = ACTIVE_BUFF2_SKILL_STAT2_RE.search(option)
            ACTIVE_BUFF2_SKILL_STAT2 += int(result.group('value'))
        except: pass

        try:
            ### 모든 직업 N 레벨 스킬 레벨 증가 ###
            result  = INC_SKILL_LV1_RE.search(option)
            value   = int(result.group('value1'))
            skillLv = int(result.group('value2'))
            if value == 30: ACTIVE_BUFF1_SKILL_LV += skillLv
            if value == 48: PASSIVE_BUFF_SKILL_LV += skillLv
            if value == 50: ACTIVE_BUFF2_SKILL_LV += skillLv
            if value == 100: ACTIVE_BUFF3_SKILL_LV += skillLv
        except: pass

        try:
            ### 모든 직업 N ~ N 레벨 스킬 레벨 증가 ###
            result = INC_SKILL_LV2_RE.search(option)
            startLv = int(result.group('value1'))
            endLv   = int(result.group('value2'))
            skillLv = int(result.group('value3'))
            if startLv <= 30 <= endLv: ACTIVE_BUFF1_SKILL_LV += skillLv
            if startLv <= 48 <= endLv: PASSIVE_BUFF_SKILL_LV += skillLv
            if startLv <= 50 <= endLv: ACTIVE_BUFF2_SKILL_LV += skillLv
            if startLv <= 100 <= endLv: ACTIVE_BUFF3_SKILL_LV += skillLv
        except: pass

        ### 헤카테 ###
        try:
            # 금단의 저주
            result = ForbiddenCurse_RE.search(option)
            ForbiddenCurseLv += int(result.group('value'))
        except: pass

        try:
            # 마리오네트
            result = MarionetteLv_RE.search(option)
            MarionetteLv += int(result.group('value'))
        except: pass

        try:
            # 소악마
            result = smallDevilLv_RE.search(option)
            smallDevilLv += int(result.group('value'))
        except: pass

    # 탈리스만 선택 신발 :: 30Lv 버프 스킬 힘, 지능 증가량 6% 추가 증가
    for i in chrBuffEquip['skill']['buff']['equipment']:
        if i['itemName'] == '탈리스만 선택':
            ACTIVE_BUFF1_SKILL_STAT += 6
            break

    ### 금단의 저주로 오르는 스탯 ###
    values = chrBuffEquip['skill']['buff']['skillInfo']['option']['values'][4:-1]
    ACTIVE_BUFF1_AD  = int((1 + chrApplyStat / 665) * int(values[0]) * (1 + ACTIVE_BUFF1_SKILL_STAT / 100))
    ACTIVE_BUFF1_AP  = int((1 + chrApplyStat / 665) * int(values[1]) * (1 + ACTIVE_BUFF1_SKILL_STAT / 100))
    ACTIVE_BUFF1_ID  = int((1 + chrApplyStat / 665) * int(values[2]) * (1 + ACTIVE_BUFF1_SKILL_STAT / 100))
    ACTIVE_BUFF1_STR = int((1 + chrApplyStat / 665) * int(values[3]) * (1 + ACTIVE_BUFF1_SKILL_STAT / 100))
    # ACTIVE_BUFF1_INT = int((1 + chrApplyStat / 665) * int(values[4]) * (1 + ACTIVE_BUFF1_SKILL_STAT / 100))

    ### 마리오네트로 오르는 스탯 ###
    ACTIVE_BUFF2_STAT = Util.getSkillValue(ACTIVE_BUFF2_INFO, chr50LvSkillLv + ACTIVE_BUFF2_SKILL_LV + MarionetteLv + 1).get('value2')
    ACTIVE_BUFF2_STAT += ACTIVE_BUFF2_SKILL_STAT1
    ACTIVE_BUFF2_STAT *= 1 + ACTIVE_BUFF2_SKILL_STAT2 / 100
    ACTIVE_BUFF2_STAT *= 1 + chrApplyStat / 750
    ACTIVE_BUFF2_STAT = int(ACTIVE_BUFF2_STAT)

    ### 종막극으로 오르는 스탯 ###
    ACTIVE_BUFF3_STAT = Util.getSkillValue(ACTIVE_BUFF3_INFO, chr100LvSkillLv + ACTIVE_BUFF3_SKILL_LV).get('value8')
    ACTIVE_BUFF3_STAT = ACTIVE_BUFF2_STAT * (ACTIVE_BUFF3_STAT / 100)
    ACTIVE_BUFF3_STAT = int(ACTIVE_BUFF3_STAT)

    ### 소악마로 오르는 스탯 ###
    PASSIVE_BUFF_STAT = Util.getSkillValue(PASSIVE_BUFF_INFO, chr48LvSkillLv + PASSIVE_BUFF_SKILL_LV + smallDevilLv).get('value3')

    ### 총 버프력 ###
    # TOTAL1 = (1 + ((15000 + ACTIVE_BUFF1_STR + ACTIVE_BUFF2_STAT + ACTIVE_BUFF3_STAT + PASSIVE_BUFF_STAT) / 250)) *\
    #         ( 2650 + ((ACTIVE_BUFF1_AD + ACTIVE_BUFF1_AP + ACTIVE_BUFF1_ID) / 3) )
    # TOTAL1 = int(TOTAL1 / 10)
    #
    # TOTAL2 = (1 + ((15000 + ACTIVE_BUFF1_STR * 1.25 + ACTIVE_BUFF2_STAT + ACTIVE_BUFF3_STAT + PASSIVE_BUFF_STAT) / 250)) *\
    #         ( 2650 + ((ACTIVE_BUFF1_AD * 1.25 + ACTIVE_BUFF1_AP * 1.25 + ACTIVE_BUFF1_ID * 1.25) / 3) )
    # TOTAL2 = int(TOTAL2 / 10)

    TOTAL = (1 + ((15000 + ACTIVE_BUFF1_STR * 1.25 * 1.15 + ACTIVE_BUFF2_STAT + ACTIVE_BUFF3_STAT + PASSIVE_BUFF_STAT) / 250)) *\
            ( 2650 + ((ACTIVE_BUFF1_AD * 1.25 * 1.15 + ACTIVE_BUFF1_AP * 1.25 * 1.15 + ACTIVE_BUFF1_ID * 1.25 * 1.15) / 3) )
    TOTAL = int(TOTAL / 10)

    ### 출력 ###
    embed = discord.Embed(title=name + '님의 버프력을 알려드릴게요!')
    embed.add_field(name='> 금단의 저주(기본)',
                    value='물리 공격력 : ' + format(ACTIVE_BUFF1_AD, ',') + '\r\n' +
                          '마법 공격력 : ' + format(ACTIVE_BUFF1_AP, ',') + '\r\n' +
                          '독립 공격력 : ' + format(ACTIVE_BUFF1_ID, ',') + '\r\n' +
                          '힘, 지능 : '    + format(ACTIVE_BUFF1_STR, ',') + '\r\n')
    embed.add_field(name='> 금단의 저주(퍼펫)',
                    value='물리 공격력 : ' + format(int(ACTIVE_BUFF1_AD * 1.25), ',') + '\r\n' +
                          '마법 공격력 : ' + format(int(ACTIVE_BUFF1_AP * 1.25), ',') + '\r\n' +
                          '독립 공격력 : ' + format(int(ACTIVE_BUFF1_ID * 1.25), ',') + '\r\n' +
                          '힘, 지능 : '    + format(int(ACTIVE_BUFF1_STR * 1.25), ','))
    embed.add_field(name='> 금단의 저주(퍼펫 + 편애)',
                    value='물리 공격력 : ' + format(int(ACTIVE_BUFF1_AD * 1.25 * 1.15), ',') + '\r\n' +
                          '마법 공격력 : ' + format(int(ACTIVE_BUFF1_AP * 1.25 * 1.15), ',') + '\r\n' +
                          '독립 공격력 : ' + format(int(ACTIVE_BUFF1_ID * 1.25 * 1.15), ',') + '\r\n' +
                          '힘, 지능 : '    + format(int(ACTIVE_BUFF1_STR * 1.25 * 1.15), ','))
    embed.add_field(name='> 마리오네트',
                    value='힘, 지능 : ' + format(ACTIVE_BUFF2_STAT, ','))
    embed.add_field(name='> 종막극',
                    value='힘, 지능 : ' + format(ACTIVE_BUFF3_STAT, ','))
    embed.add_field(name='> 소악마',
                    value='힘, 지능 : ' + format(PASSIVE_BUFF_STAT, ','))
    embed.add_field(name='> 버프력',
                    value=format(TOTAL, ','))
    embed.set_footer(text='실제 버프 수치와 결과값이 다를 수 있어요!')
    await ctx.channel.send(embed=embed)
