# 디스코드
import discord
from discord.ext import commands

# API
import DNFAPI

# 기타
import re
import Util
import Classes
from datetime import datetime

### 기본설정 ###
bot = commands.Bot(command_prefix='!')
token = 'NzgyMTc4NTQ4MTg1NTYzMTQ3.X8Iaig.0o0wUqoz8j_iub3SC7A5SFY83U4'
#token = 'NzgxNzgyNzQ5NDc5Njk4NDQy.X8Cp7A.wJ69VOJUvfEMnv6-F63QG8KNans'
epic = Classes.epicRank()
setRank = Classes.setRank()

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
                           "#시크봇의 명령어들을 알려드릴게요!\r\n"
                           "#최근 업데이트 날짜 : 2020/12/22                    #건의사항 : LaivY#2463\r\n"
                           "──────────────────────────────────검색──────────────────────────────────\r\n"
                           "'!등급' : 오늘의 장비 등급을 알려드릴게요.\r\n"
                           "'!캐릭터 <닉네임>' : 캐릭터가 장착한 장비와 세트를 알려드릴게요.\r\n"
                           "'!장비 <장비아이템이름>' : 궁금하신 장비템의 옵션을 검색해서 알려드릴게요.\r\n"
                           "'!세트 <세트아이템이름>' : 궁금하신 세트템의 옵션을 검색해서 알려드릴게요.\r\n"
                           "\r\n──────────────────────────────────랭킹──────────────────────────────────\r\n"
                           "'!획득에픽 <닉네임>' : 캐릭터가 이번 달에 획득한 에픽을 알려드릴게요.\r\n"
                           "'!상세정보 <닉네임>' : 캐릭터의 공격력 증가치를 알려드릴게요. 효율이랑요!\r\n"
                           "'!기린랭킹' : 이번 달에 에픽을 많이 먹은 기린을 박제해놨어요! 나만운업서!\r\n"
                           "'!세팅랭킹' : 캐릭터의 상세정보를 기반으로한 세팅 점수 랭킹을 보여드릴게요.\r\n"
                           "\r\n──────────────────────────────────기타──────────────────────────────────\r\n"
                           "'!청소' : 시크봇이 말한 것들을 모두 삭제할게요.\r\n"
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
                          description=str(itemDetailInfo['itemAvailableLevel']) + 'Lv ' + itemDetailInfo[
                              'itemRarity'] + ' ' + itemDetailInfo['itemTypeDetail'])
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
    embed = discord.Embed(title=setItemName + '의 정보를 알려드릴게요.')
    for i in setItemInfoList:
        embed.add_field(name='> ' + i['itemRarity'] + ' ' + i['slotName'], value=i['itemName'] + '\r\n')
    for i in setItemOptionList:
        embed.add_field(name='> ' + str(i['optionNo']) + '세트 옵션', value=i['explain'])
    itemImageUrl = DNFAPI.getItemImageUrl(setItemInfoList[0]['itemId'])
    embed.set_thumbnail(url=itemImageUrl)

    await ctx.channel.send(embed=embed)

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
        end = min(start + 15, len(chrTimeLineData))

        if start == 0:
            embed = discord.Embed(title=name + '님이 이번 달에 획득한 에픽을 알려드릴게요!',
                                  description='총 ' + str(len(chrTimeLineData)) + '개의 에픽을 획득하셨네요!')
        else:
            embed = discord.Embed(title=str(start + 1) + ' ~ ' + str(end) + '번째 획득한 에픽들')

        for i in chrTimeLineData[start:end]:
            embed.add_field(
                name='> ' + i['date'][:10] + '\r\n> ch' + str(i['data']['channelNo']) + '.' + i['data']['channelName'],
                value=i['data']['itemName'])
        await ctx.channel.send(embed=embed)

        index += 15

    # 데이터 저장
    today = datetime.today()
    epic.add(chrId, [today.year, today.month, server, name, len(chrTimeLineData)])

@bot.command()
async def 상세정보(ctx, name='None'):
    if name == 'None':
        await ctx.channel.send('> !상세정보 <닉네임> 의 형태로 적어야해요!')
        return

    # 검색
    try:
        chrIdList = DNFAPI.getChrIdList('전체', name)
        server, chrId, name = await Util.getSelectionFromChrIdList(bot, ctx, chrIdList)
    except:
        return False

    itemIdList = DNFAPI.getChrEquipItemIdList(server, chrId)
    chrEquipCreatureId = DNFAPI.getChrEquipCreatureId(server, chrId)
    if chrEquipCreatureId is not None: itemIdList.append(chrEquipCreatureId)

    ### 정규식 설정 ###
    rDmgInc       = re.compile('공격시데미지(?P<value>\d+)%증가')
    rCriDmgInc    = re.compile('크리티컬공격시데미지(?P<value>\d+)%증가')
    rCriDmgInc2   = re.compile('크리티컬데미지(?P<value>\d+)%증가')
    rAddDmgInc    = re.compile('공격시데미지증가\S(?P<value>\d+)%추가증가')
    rAddCriDmgInc = re.compile('크리티컬공격시데미지증가\S(?P<value>\d+)%추가증가')
    rAddDmg       = re.compile('공격시(?P<value>\d+)%추가데미지')
    rEleAddDmg    = re.compile('공격시(?P<value>\d+)%속성추가데미지')
    rAllDmgInc    = re.compile('모든공격력(?P<value>\d+)%증가')
    rSkillDmgInc  = re.compile('스킬공격력(?P<value>\d+)%증가')
    rAdApInInc    = re.compile('물리,마법,독립공격력(?P<value>\d+)%')
    rStrIntInc    = re.compile('힘,지능(?P<value>\d+)%증가')
    rContinueDmg  = re.compile('적에게입힌피해의(?P<value>\d+)%만큼')
    ### 정규식 설정 끝 ###

    ### 변수 설정 ###
    dmgInc       = 0 # 데미지 증가
    addDmgInc    = 0 # 데미지 추가 증가
    criDmgInc    = 0 # 크리티컬 데미지 증가
    addCriDmgInc = 0 # 크리티컬 데미지 추가 증가
    addDmg       = 0 # 추가 데미지
    eleAddDmg    = 0 # 속성 추가 데미지
    allDmgInc    = 0 # 모든 공격력 증가
    skillDmgInc  = 1 # 스킬 데미지 증가
    adApInInc    = 0 # 물리,마법, 독립 공격력 증가
    strIntInc    = 0 # 힘, 지능 증가
    continueDmg  = 0 # 지속피해

    indiElement  = {'화' : 0, '수' : 0, '명' : 0, '암' : 0}
    element      = 0 # 모든 속성 강화
    elementResist= 0 # 암속성 저항
    ### 선언 끝 ###

    ### 속성 강화 :: 가장 높은 수치 ###
    chrStatInfo = DNFAPI.getChrStatInfo(server, chrId)
    r = re.compile('(?P<key>\S)속성 강화')
    for i in chrStatInfo:
        if i['name'] == '암속성 저항':
            elementResist = i['value']

        result = r.search(i['name'])
        if result is not None:
            indiElement[result.group('key')] = i['value']

    # 이 변수에 옵션들을 저장해서 계산함
    info = []

    ### 먼동 :: 강화 수치에 따라 옵션 설정
    chrEquipItemList, chrEquipItemEnchantInfo = DNFAPI.getChrEquipItemInfoList(server, chrId)
    for i in range(len(chrEquipItemList)):
        itemName = DNFAPI.getItemDetail(chrEquipItemList[i])['itemName']
        if itemName == '새벽을 녹이는 따스함':
            info.append('모든 공격력 6% 증가')
            info.append('스킬 공격력 ' + str(4 + chrEquipItemEnchantInfo[i]['reinforce']) + '% 증가')

        elif itemName == '달빛을 가두는 여명':
            info.append('물리, 마법, 독립 공격력 6% 증가')
            info.append('힘, 지능 ' + str(4 + chrEquipItemEnchantInfo[i]['reinforce']) + '% 증가')

        elif itemName == '새벽을 감싸는 따스함':
            info.append('모든 공격력 6% 증가')
            info.append('스킬 공격력 ' + str(4 + chrEquipItemEnchantInfo[i]['reinforce']) + '% 증가')

        elif itemName == '고요를 머금은 이슬':
            info.append('공격 시 데미지 증가량 ' + str(4 + chrEquipItemEnchantInfo[i]['reinforce']) + '% 추가 증가')

    ### 아이템 옵션 계산 ###
    for itemId in itemIdList:
        itemDetailInfo = DNFAPI.getItemDetail(itemId)

        # 별의 바다 : 바드나후 :: 속추뎀 20퍼로 환산
        if itemDetailInfo['itemName'] == '별의 바다 : 바드나후':
            info.append('공격 시 20% 속성 추가 데미지')

        # 순백의 기도 :: 속성 강화 버프, 물마독 증가
        if itemDetailInfo['itemName'] == '순백의 기도':
            element += 26
            info.append('물리, 마법, 독립 공격력 15% 증가')

        # 임의 선택 :: 모든 공격력 증가 35%로 적용
        if itemDetailInfo['itemName'] == '임의 선택':
            info.append('모든 공격력 35% 증가')
            continue

        # 합리적 선택 :: 물마독 20%만 적용
        if itemDetailInfo['itemName'] == '합리적 선택':
            info.append('물리, 마법, 독립 공격력 20% 증가')
            continue

        # 탈리스만 선택 :: 추뎀 17%만 적용
        if itemDetailInfo['itemName'] == '탈리스만 선택':
            info.append('공격 시 17% 추가 데미지')
            continue

        # 베테랑 세트 :: 숙련 등급 전설 기준
        if itemDetailInfo['itemName'] == '전장의 매':
            info.append('물리, 마법, 독립 공격력 34% 증가')
            continue

        if itemDetailInfo['itemName'] == '퀘이크 프론':
            info.append('스킬 공격력 34% 증가')
            continue

        if itemDetailInfo['itemName'] == '오퍼레이션 델타':
            element += 68
            continue

        if itemDetailInfo['itemName'] == '데파르망':
            info.append('크리티컬 공격 시 데미지 증가량 34% 추가 증가')
            continue
            
        if itemDetailInfo['itemName'] == '전쟁의 시작':
            info.append('힘, 지능 34% 증가')
            continue

        # 전자기 진공관 :: 속성 강화 버프
        if itemDetailInfo['itemName'] == '전자기 진공관':
            element += 40

        # 대자연
        if  itemDetailInfo['itemName'] == '포용의 굳건한 대지' or \
            itemDetailInfo['itemName'] == '원시 태동의 대지':
            element += 24

        if itemDetailInfo['itemName'] == '맹렬히 타오르는 화염':
            indiElement['화'] = indiElement['화'] + 24

        if itemDetailInfo['itemName'] == '잠식된 신록의 숨결':
            indiElement['암'] = indiElement['암'] + 24

        if itemDetailInfo['itemName'] == '잔잔한 청록의 물결':
            indiElement['수'] = indiElement['수'] + 24

        if itemDetailInfo['itemName'] == '휘감는 햇살의 바람':
            indiElement['명'] = indiElement['명'] + 24

        # 마법사 [???]의 하의 :: 속성 강화, 물마독 증가
        if itemDetailInfo['itemName'] == '마법사 [???]의 하의':
            element += 18
            elementResist += 18
            info.append('물리, 마법, 독립 공격력 10% 증가')

        # 종말의 역전 :: 비통한 자의 목걸이, 비운의 유물 착용 시 물마독 10% 감소
        if itemDetailInfo['itemName'] == '종말의 역전':
            if 'da5e4132290136b6bae3d1d8e2692446' in itemIdList: adApInInc -= 10
            if '33727ea5e4d52bf641bd15ba2556bc75' in itemIdList: adApInInc -= 10

        # 군신의 숨겨진 유산 세트 :: 2세트 옵션을 여기서 계산
        if  itemDetailInfo['itemName'] == '군신의 유언장' and \
            ('e8339821b962569895a1dcd569ef1ed8' in itemIdList or 'e98db581d86ffc2098c66049b019cf83' in itemIdList):
            info.append('크리티컬 공격 시 데미지 증가량 5% 추가 증가')

        # 심연에 빠진 검은 셔츠 :: 속성 저항에 따라 설정
        if itemDetailInfo['itemName'] in ['심연에 빠진 검은 셔츠', '고대 심연의 로브']:
            count = min(elementResist / 10, 5)
            info.append('모든 공격력 ' + str(7 * count) + '% 증가')
            continue

        # 타락한 세계수의 생명 :: 속성 저항에 따라 설정
        if itemDetailInfo['itemName'] == '타락한 세계수의 생명':
            count = min(elementResist / 13, 4)
            info.append('힘, 지능 ' + str(10 * count) + '% 증가')
            continue

        # 암흑술사가 직접 저술한 고서 :: 속성 저항에 따라 설정
        if itemDetailInfo['itemName'] == '암흑술사가 직접 저술한 고서':
            count = min(elementResist / 7, 7)
            info.append('물리, 마법, 독립 공격력 ' + str(6 * count) + '% 증가')
            continue

        # 어둠을 파헤치는 바지 :: 속성 저항에 따라 설정
        if itemDetailInfo['itemName'] == '어둠을 파헤치는 바지':
            count = min(elementResist / 14, 5)
            info.append('공격 시 데미지 증가량 ' + str(7 * count) + '% 추가 증가')
            continue

        # 지독한 집념의 탐구 :: 속성 저항에 따라 설정
        if itemDetailInfo['itemName'] in ['지독한 집념의 탐구', '영원히 끝나지 않는 탐구']:
            count = min(elementResist / 18, 4)
            info.append('모든 공격력 ' + str(7 * count) + '% 증가')
            element += 10 * count
            continue

        # 암흑술사의 정수 :: 속성 저항에 따라 설정
        if itemDetailInfo['itemName'] == '암흑술사의 정수':
            count = min(elementResist / 10, 7)
            info.append('크리티컬 공격 시 데미지 증가량 ' + str(5 * count) + '% 추가 증가')
            info.append('스킬 공격력 ' + str(count) + '% 증가')
            continue

        # 나락으로 빠진 발 :: 속성 저항에 따라 설정
        if itemDetailInfo['itemName'] == '나락으로 빠진 발':
            count = min(elementResist / 3, 5)
            element += 14 * count
            continue

        # 어둠을 지배하는 고리 :: 속성 저항에 따라 설정
        if itemDetailInfo['itemName'] == '어둠을 지배하는 고리':
            count = min(elementResist / 4, 4)
            info.append('크리티컬 공격 시 데미지 증가량 ' + str(10 * count) + '% 추가 증가')
            continue
            
        # 끝없는 나락의 다크버스 :: 속성 저항에 따라 설정
        if itemDetailInfo['itemName'] in ['끝없는 나락의 다크버스', '영원한 나락의 다크버스']:
            count = min(elementResist / 3, 6)
            info.append('모든 공격력 ' + str(7 * count) + '% 증가')
            continue

        # 먼동 세트 :: 이미 계산했으므로 패스
        if itemDetailInfo['setItemName'] == '먼동 틀 무렵 세트':
            continue

        # 영보 :: 버프
        if itemDetailInfo['setItemName'] == '영보 : 세상의 진리 세트':
            element += 40

        # 사막 :: 퀵슬롯 6개 비운것을 기준
        if itemDetailInfo['setItemName'] == '메마른 사막의 유산 세트':
            info.append('공격 시 데미지 증가량 5% 추가 증가')

        # 나머지
        options = itemDetailInfo['itemExplainDetail'].split('\n')
        for i in options:
            # 예외처리 :: 특정 스킬 데미지 증가
            exception = re.compile('\d+ 레벨 액티브 스킬 공격력 \d+% 증가')
            if exception.search(i) is not None: continue

            info.append(i)

    ### 신화 옵션 계산 ###
    setItemId = []
    chrEquipItemInfo = DNFAPI.getChrEquipItemInfo(server, chrId)
    for i in chrEquipItemInfo:
        if i['setItemId'] is not None:
            setItemId.append(i['setItemId'])

        # 신화 옵션
        try:
            for j in i['mythologyInfo']['options']:
                info.append(j['explain'])
        except: pass

    ### 시로코 옵션 계산 ###
    chrSirocoItemInfo = Util.getSirocoItemInfo(chrEquipItemInfo)
    if chrSirocoItemInfo is not None:
        # 1세트 옵션
        for k in chrSirocoItemInfo.keys():
            try:
                info.append(chrSirocoItemInfo[k]['1옵션'])
            except: pass

        # 2세트 옵션
        # 잔향
        if 3 in chrSirocoItemInfo['세트'].values():
            info.append(chrSirocoItemInfo['잔향']['2옵션'])

        # 넥스
        if  '무형 : 넥스의 잠식된 의복' in chrSirocoItemInfo.keys() and \
            '무의식 : 넥스의 몽환의 어둠' in chrSirocoItemInfo.keys():
            info.append(chrSirocoItemInfo['무형 : 넥스의 잠식된 의복']['2옵션'])
        if '무의식 : 넥스의 몽환의 어둠' in chrSirocoItemInfo.keys() and \
            '환영 : 넥스의 검은 기운' in chrSirocoItemInfo.keys():
            info.append(chrSirocoItemInfo['무의식 : 넥스의 몽환의 어둠']['2옵션'])
        if '환영 : 넥스의 검은 기운' in chrSirocoItemInfo.keys() and \
            '무형 : 넥스의 잠식된 의복' in chrSirocoItemInfo.keys():
            info.append(chrSirocoItemInfo['환영 : 넥스의 검은 기운']['2옵션'])

        # 암살자
        if  '무형 : 암살자의 잠식된 의식' in chrSirocoItemInfo.keys() and \
            '무의식 : 암살자의 몽환의 흔적' in chrSirocoItemInfo.keys():
            info.append(chrSirocoItemInfo['무형 : 암살자의 잠식된 의식']['2옵션'])

        if '무의식 : 암살자의 몽환의 흔적' in chrSirocoItemInfo.keys() and \
            '환영 : 암살자의 검은 검집' in chrSirocoItemInfo.keys():
            info.append(chrSirocoItemInfo['무의식 : 암살자의 몽환의 흔적']['2옵션'])

        if '환영 : 암살자의 검은 검집' in chrSirocoItemInfo.keys() and \
            '무형 : 암살자의 잠식된 의식' in chrSirocoItemInfo.keys():
            info.append(chrSirocoItemInfo['환영 : 암살자의 검은 검집']['2옵션'])

        # 수문장
        if  '무형 : 수문장의 잠식된 갑주' in chrSirocoItemInfo.keys() and \
            '무의식 : 수문장의 몽환의 사념' in chrSirocoItemInfo.keys():
            element += 30
        if  '무의식 : 수문장의 몽환의 사념' in chrSirocoItemInfo.keys() and \
            '환영 : 수문장의 검은 가면' in chrSirocoItemInfo.keys():
            element += 30
        if  '환영 : 수문장의 검은 가면' in chrSirocoItemInfo.keys() and \
            '무형 : 수문장의 잠식된 갑주' in chrSirocoItemInfo.keys():
            element += 30

        # 로도스
        if  '무형 : 로도스의 잠식된 의지' in chrSirocoItemInfo.keys() and \
            '무의식 : 로도스의 몽환의 근원' in chrSirocoItemInfo.keys():
            info.append(chrSirocoItemInfo.get('무형 : 로도스의 잠식된 의지')['2옵션'])
        if '무의식 : 로도스의 몽환의 근원' in chrSirocoItemInfo.keys() and \
            '환영 : 로도스의 검은 핵' in chrSirocoItemInfo.keys():
            info.append(chrSirocoItemInfo.get('무의식 : 로도스의 몽환의 근원')['2옵션'])
        if '환영 : 로도스의 검은 핵' in chrSirocoItemInfo.keys() and \
            '무형 : 로도스의 잠식된 의지' in chrSirocoItemInfo.keys():
            info.append(chrSirocoItemInfo.get('환영 : 로도스의 검은 핵')['2옵션'])

    ### 세트 갯수 계산 ###
    chrEquipSetItemAmount = {}
    for i in setItemId:
        SET = 0
        if chrEquipSetItemAmount.get(i) is not None:
            SET = chrEquipSetItemAmount.get(i)
        chrEquipSetItemAmount.update({i : SET + 1})

    ### 세트 옵션 계산 ###
    for i in chrEquipSetItemAmount.keys():
        for j in DNFAPI.getSetItemInfoList(i)[1]:
            if j['optionNo'] <= chrEquipSetItemAmount.get(i):
                # 행운의 트라이앵글 :: 77 기준
                if i == '9b2a1398222c5ead60edc99cf959338a' and j['optionNo'] == 3:
                    info.append('스킬 공격력 31% 증가')
                    continue

                # 운명의 주사위 :: 6 기준
                if i == '5742ec75674086d001067005f43f0da4' and j['optionNo'] == 3:
                    info.append('힘, 지능 14% 증가')
                    continue

                # 메마른 사막의 유산 2세트 :: 퀵슬롯 6개 비운것 기준
                if i == '0ff0e427a3746948c27de4af1d943109' and j['optionNo'] == 2:
                    info.append('물리, 마법, 독립 공격력 22% 증가')
                    info.append('스킬 공격력 6% 증가')
                    continue

                # 베테랑 군인의 정복 5세트 :: 숙련 등급 전설 기준
                if i == '10c2cee96ec4093136d041f7f40b7bff' and j['optionNo'] == 5:
                    info.append('공격 시 40% 추가 데미지')
                    continue

                # 흑마술 탐구자 세트 :: 암속성 저항에 따라 설정
                if i == '1d4ed1e13b380593c889feef9ec2f62d':
                    if j['optionNo'] == 2 and elementResist >= 76:
                        info.append('공격 시 데미지 증가량 12% 추가 증가')
                        info.append('스킬 공격력 10% 증가')
                        continue
                    if j['optionNo'] == 3 and elementResist >= 81:
                        info.append('공격 시 13% 속성 추가 데미지')
                        continue

                # 나락의 구도자 세트 :: 암속성 저항에 따라 설정
                if i == 'f51b430435a8383b3cf6d34407c4a553':
                    if j['optionNo'] == 2 and elementResist >= 21:
                        info.append('모든 공격력 10% 증가')
                        info.append('공격 시 10% 추가 데미지')
                        continue
                    if j['optionNo'] == 3:
                        count = min(elementResist / 7, 4)
                        info.append('스킬 공격력 ' + str(4 * count) + '% 증가')
                        element += 10 * count
                        continue

                # 군신의 숨겨진 유산 2세트 :: 크추뎀은 이미 계산함
                if i == '0d7fa7e5f82d8ec524d1b8202b31497f' and j['optionNo'] == 2:
                    info.append('물리, 마법, 독립 공격력 10% 증가')
                    info.append('모든 공격력 8% 증가')
                    continue

                # 군신의 숨겨진 유산 3세트 :: 이동속도 최대 기준
                if i == '0d7fa7e5f82d8ec524d1b8202b31497f' and j['optionNo'] == 3:
                    info.append('스킬 공격력 10% 증가')
                    info.append('힘, 지능 10% 증가')
                    continue

                # 나머지
                temp = j['explain'].replace('\r', '')
                temp = temp.split('\n')
                info += temp

    ### 계산 ###
    for i in info:
        i = i.replace(' ', '')

        # 데미지, 크리티컬 데미지 증가
        tCriDmgInc = rCriDmgInc.search(i)
        tCriDmgInc2 = rCriDmgInc2.search(i)
        if tCriDmgInc is not None and criDmgInc < int(tCriDmgInc.group('value')):
            criDmgInc = int(tCriDmgInc.group('value'))
        elif tCriDmgInc2 is not None and criDmgInc < int(tCriDmgInc2.group('value')):
            criDmgInc = int(tCriDmgInc2.group('value'))
        else:
            tDmgInc = rDmgInc.search(i)
            if tDmgInc is not None and dmgInc < int(tDmgInc.group('value')):
                dmgInc = int(tDmgInc.group('value'))

        # 데미지, 크리티컬 데미지 추가 증가
        tAddCriDmgInc = rAddCriDmgInc.search(i)
        if tAddCriDmgInc is not None:
            addCriDmgInc += int(tAddCriDmgInc.group('value'))
        else:
            tAddDmgInc = rAddDmgInc.search(i)
            if tAddDmgInc is not None:
                addDmgInc += int(tAddDmgInc.group('value'))

        # 추가 데미지
        tAddDmg = rAddDmg.search(i)
        if tAddDmg is not None:
            addDmg += int(tAddDmg.group('value'))

        # 속성 추가 데미지
        tEleDmg = rEleAddDmg.search(i)
        if tEleDmg is not None:
            eleAddDmg += int(tEleDmg.group('value'))

        # 모든 공격력 증가
        tAllDmgInc = rAllDmgInc.search(i)
        if tAllDmgInc is not None:
            allDmgInc += int(tAllDmgInc.group('value'))

        # 스킬 데미지 증가
        tSkillDmgInc = rSkillDmgInc.search(i)
        if tSkillDmgInc is not None:
            skillDmgInc *= 1 + float(tSkillDmgInc.group('value')) / 100

        # 물마독 증가
        tAdAPInInc = rAdApInInc.search(i)
        if tAdAPInInc is not None:
            adApInInc += int(tAdAPInInc.group('value'))

        # 힘지능 증가
        tStrIntInc = rStrIntInc.search(i)
        if tStrIntInc is not None:
            strIntInc += int(tStrIntInc.group('value'))

        # 지속 피해
        tContinueDmg = rContinueDmg.search(i)
        if tContinueDmg is not None:
            continueDmg += int(tContinueDmg.group('value'))

    # 모든 속성 강화 += 속성 강화 중 가장 큰 값
    element += max(indiElement.values())
    
    # 속추뎀 -> 추뎀 변환
    eleAddDmg = int(eleAddDmg * (1.05 + 0.0045 * element))

    # 스증뎀 변환
    skillDmgInc = round((skillDmgInc - 1) * 100)
    if skillDmgInc == 1:
        skillDmgInc = 0

    # 데미지 계산
    damage = Util.getFinalDamage(dmgInc, addDmgInc, criDmgInc, addCriDmgInc, addDmgInc, eleAddDmg, allDmgInc, adApInInc, strIntInc, element, skillDmgInc, continueDmg)

    # 랭킹 추가
    setRank.add(chrId, [server, name, damage])

    embed = discord.Embed(title=name + '님의 상세정보를 알려드릴게요.')
    embed.add_field(name='> 데미지 증가',              value=str(dmgInc + addDmgInc) + '%')
    embed.add_field(name='> 크리티컬 데미지 증가',     value=str(criDmgInc + addCriDmgInc) + '%')
    embed.add_field(name='> 추가 데미지',              value=str(addDmg + eleAddDmg) + '% (' + str(addDmg) + '% + ' + str(eleAddDmg) + '%)')
    embed.add_field(name='> 모든 공격력 증가',         value=str(allDmgInc) + '%')
    embed.add_field(name='> 스킬 데미지 증가',         value=str(skillDmgInc) + '%')
    embed.add_field(name='> 물리마법독립 공격력 증가', value=str(adApInInc) + '%')
    embed.add_field(name='> 힘, 지능 증가',            value=str(strIntInc) + '%')
    embed.add_field(name='> 지속 피해',                value=str(continueDmg) + '%')
    embed.add_field(name='> 세팅 점수',                value=str(damage) + '점')
    embed.set_footer(text='세팅 점수는 제작자 마음대로 세운 공식이기 때문에 재미로만 봐주세요!')
    await ctx.channel.send(embed=embed)
    
    # 데미지 효율 계산
    embed2 = discord.Embed(title='각 능력치 별 효율도 알려드릴게요.')

    dmgInc10 = Util.getFinalDamage(dmgInc, addDmgInc + 10, criDmgInc, addCriDmgInc, addDmgInc, eleAddDmg, allDmgInc, adApInInc, strIntInc, element, skillDmgInc, continueDmg)
    embed2.add_field(name='> 데미지 10%', value='최종 데미지 ' + str(round((dmgInc10 / damage - 1) * 1000) / 10) + '% 증가')

    criDmgInc10 = Util.getFinalDamage(dmgInc, addDmgInc, criDmgInc, addCriDmgInc + 10, addDmgInc, eleAddDmg, allDmgInc, adApInInc, strIntInc, element, skillDmgInc, continueDmg)
    embed2.add_field(name='> 크리티컬 데미지 10%', value='최종 데미지 ' + str(round((criDmgInc10 / damage - 1) * 1000) / 10) + '% 증가')

    addDmgInc10 = Util.getFinalDamage(dmgInc, addDmgInc, criDmgInc, addCriDmgInc, addDmgInc + 10, eleAddDmg, allDmgInc, adApInInc, strIntInc, element, skillDmgInc, continueDmg)
    embed2.add_field(name='> 추가 데미지 10%', value='최종 데미지 ' + str(round((addDmgInc10 / damage - 1) * 1000) / 10) + '% 증가')
    
    allDmgInc10 = Util.getFinalDamage(dmgInc, addDmgInc, criDmgInc, addCriDmgInc, addDmgInc, eleAddDmg, allDmgInc + 10, adApInInc, strIntInc, element, skillDmgInc, continueDmg)
    embed2.add_field(name='> 모든 공격력 10%', value='최종 데미지 ' + str(round((allDmgInc10 / damage - 1) * 1000) / 10) + '% 증가')

    skillDmgInc10 = int(damage * 1.1)
    embed2.add_field(name='> 스킬 데미지 10%', value='최종 데미지 ' + str(round((skillDmgInc10 / damage - 1) * 1000) / 10) + '% 증가')
    
    adApInInc10 = Util.getFinalDamage(dmgInc, addDmgInc, criDmgInc, addCriDmgInc, addDmgInc, eleAddDmg, allDmgInc, adApInInc + 10, strIntInc, element, skillDmgInc, continueDmg)
    embed2.add_field(name='> 물리마법독립 10%', value='최종 데미지 ' + str(round((adApInInc10 / damage - 1) * 1000) / 10) + '% 증가')
    
    strIntInc10 = Util.getFinalDamage(dmgInc, addDmgInc, criDmgInc, addCriDmgInc, addDmgInc, eleAddDmg, allDmgInc, adApInInc, strIntInc + 10, element, skillDmgInc, continueDmg)
    embed2.add_field(name='> 힘, 지능 10%', value='최종 데미지 ' + str(round((strIntInc10 / damage - 1) * 1000) / 10) + '% 증가')

    continueDmgInc10 = Util.getFinalDamage(dmgInc, addDmgInc, criDmgInc, addCriDmgInc, addDmgInc, eleAddDmg, allDmgInc, adApInInc, strIntInc, element, skillDmgInc, continueDmg + 10)
    embed2.add_field(name='> 지속 데미지 10%', value='최종 데미지 ' + str(round((continueDmgInc10 / damage - 1) * 1000) / 10) + '% 증가')
    embed2.set_footer(text='이 수치들은 참고만 해주세요! 오차가 있을 수 있어요.')
    await ctx.channel.send(embed=embed2)

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
async def 세팅랭킹(ctx):
    embed = discord.Embed(title='세팅 랭킹을 알려드릴게요!',description='랭킹은 15등까지만 보여드려요.')
    embed.set_footer(text='열심히 개발중이라 랭킹이 자주 초기화될 수 있어요.')
    rank = 1
    for k in setRank.data.keys():
        embed.add_field(name='> ' + str(rank) + '등\r\n> ' + setRank.data[k][0] + ' ' + setRank.data[k][1], value=str(setRank.data[k][2]) + '점')
        rank += 1

    if rank == 1:
        embed.add_field(name='> 랭킹에 아무도 없어요!', value='> !상세정보 <닉네임> 으로 자신의 캐릭터를 랭킹에 추가해보세요!')

    await ctx.channel.purge(limit=1)
    await ctx.channel.send(embed=embed)

@bot.command()
async def 청소(ctx):
    await ctx.channel.purge(limit=1)
    async for message in ctx.channel.history(limit=200):
        def check(m): return m.author == bot.user
        await ctx.channel.purge(limit=100, check=check)

### 제작자 명령어 ###
@bot.command()
async def 연결(ctx):
    if ctx.message.author.id == 247361856904232960:
        await ctx.channel.purge(limit=1)
        await ctx.channel.send('> 시크봇은 ' + str(len(bot.guilds)) + '개의 서버에 연결되어있어요!')
        # index = 0
        # while index < NUMBER_OF_CONNECTED_SERVER:
        #     start = index
        #     end   = min(len(bot.guilds), index + 15)
        #
        #     if start == 0:
        #         title = str(NUMBER_OF_CONNECTED_SERVER) + '개의 서버에 시크봇이 연결되어있어요!\r\n' + str(start + 1) + ' ~ ' + str(end) + '번째 서버 목록'
        #     else:
        #         title = str(start + 1) + ' ~ ' + str(end) + '번째 서버 목록'
        #     embed = discord.Embed(title=title)
        #
        #     # 출력
        #     for i in bot.guilds[start:end]:
        #         embed.add_field(name='> ' + i.name, value=str(i.member_count) + '명')
        #     await ctx.channel.send(embed=embed)
        #
        #     index += 15

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
