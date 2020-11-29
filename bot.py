import discord
from discord.ext import commands
import asyncio

import DNFAPI
import requests
import re

# 기본설정
bot = commands.Bot(command_prefix='!')
token = 'NzgxNzgyNzQ5NDc5Njk4NDQy.X8Cp7A.wJ69VOJUvfEMnv6-F63QG8KNans'

@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('명령을 대기'))
    print('구동 완료')

@bot.event
async def on_message(msg):
    if msg.author.bot:
        return None

    await bot.process_commands(msg)

@bot.command()
async def 도움말(ctx):
    await ctx.channel.send("```cs\r\n" +
                           "#시크봇의 명령어들을 알려드릴게요!\r\n" +
                           "'!등급' : 오늘의 장비 등급을 알려드릴게요.\r\n" +
                           "'!기린력 <서버> <닉네임>' : 캐릭터가 얼마나 기린인지 알려드릴게요.\r\n" +
                           "'!캐릭터 <닉네임>' : 캐릭터가 장착한 장비와 세트를 알려드릴게요.\r\n"
                           "'!장비 <장비아이템이름>' : 궁금하신 장비템의 옵션을 검색해서 알려드릴게요.\r\n"
                           "'!세트 <세트아이템이름>' : 궁금하신 세트템의 옵션을 검색해서 알려드릴게요.\r\n"
                           "```")

@bot.command()
async def 기린력(ctx, server='None', name='None'):
    if (server == 'None' or name == 'None'):
        await ctx.channel.send('> !기린력 <서버> <닉네임> 의 형태로 적어야해요!')
        return

    await ctx.channel.send('> ' + name + '님의 기린력을 측정하고 있어요!')

    # URL만들기
    url = 'http://duntoki.xyz/giraffe?serverNm=' + server + '&charNm=' + name
    response = requests.get(url=url)
    if response.status_code == 200:
        # 패턴 정의
        pat1 = [None, None, None, None]
        pat1[0] = re.compile('(?P<date>\d\d\d\d-\d\d-\d\d) 대비-(?P<delta>\d.\d\d점 하락)')
        pat1[1] = re.compile('(?P<date>\d\d\d\d-\d\d-\d\d) 대비-(?P<delta>\d\d.\d\d점 하락)')
        pat1[2] = re.compile('(?P<date>\d\d\d\d-\d\d-\d\d) 대비(?P<delta>\d.\d\d점 상승)')
        pat1[3] = re.compile('(?P<date>\d\d\d\d-\d\d-\d\d) 대비(?P<delta>\d\d.\d\d점 상승)')

        pat2 = [None, None, None]
        pat2[0] = re.compile('<td>(?P<grade>\d\.\d점)</td>')
        pat2[1] = re.compile('<td>(?P<grade>\d\.\d\d점)</td>')
        pat2[2] = re.compile('<td>(?P<grade>\d\d\.\d\d점)</td>')

        # 결과
        result0 = None
        for i in range(4):
            result0 = pat1[i].search(response.text)
            if result0 != None: break

        result1 = None
        for i in range(3):
            result1 = pat2[i].search(response.text)
            if result1 != None: break

        # 출력
        await ctx.channel.purge(limit=1)
        try:
            await ctx.channel.purge(limit=1)
            if result0 is not None:
                embed = discord.Embed(title='기린력 측정 결과가 나왔어요!',
                                      description=name + '님의 기린력은 ' + result0.group('date') + '때 보다 ' + result0.group('delta') + '한 ' + result1.group('grade') + '입예요!')
                await ctx.channel.send(embed=embed)
            else:
                embed = discord.Embed(title='기린력 측정 결과가 나왔어요!',
                                      description=name + '님의 기린력은 변함없이 ' + result1.group('grade') + '이예요!')
                await ctx.channel.send(embed=embed)
        except:
            await ctx.channel.send('기린력을 읽어오지 못했어...')
    else:
        await ctx.channel.send('뭔가 오류가 났어...')

@bot.command()
async def 등급(ctx):
    url = 'http://dnfnow.xyz/class'
    response = requests.get(url=url)

    # 계산
    pat = []
    pat.append(re.compile('<span class="badge badge-warning">'))
    pat.append(re.compile('</span>'))

    temp0 = pat[0].search(response.text)
    start0, end0 = temp0.start(), temp0.end()

    temp1 = pat[1].search(response.text[end0:])
    start1, end1 = temp1.start(), temp1.end()

    result = response.text[end0 + 1 : end0 + start1 - 1].replace(' ', '').replace('\n', '')

    # 출력
    embed = discord.Embed(title='아이템 등급을 알려드릴게요!', description='오늘의 등급은 천공의 유산 - 소검을 기준으로 ' + result + '이예요!')
    await ctx.channel.send(embed=embed)

@bot.command()
async def 캐릭터(ctx, name='None'):
    if name == 'None':
        await ctx.channel.send('> !캐릭터 <닉네임> 의 형태로 적어야해요!')
        return

    chrIdList = DNFAPI.getChrIdList('전체', name)
    if len(chrIdList) >= 2:
        await ctx.channel.purge(limit=1)
        embed = discord.Embed(title='알고싶은 캐릭터의 번호를 입력해주세요!', description='15초만 기다려드릴거에요. 빠르게 골라주세요!')
        for i in range(len(chrIdList)):
            value = 'Lv. ' + chrIdList[i]['level'] + ' ' + chrIdList[i]['characterName'] + '\r\n' + \
                    chrIdList[i]['server'] + ' | ' + chrIdList[i]['jobGrowName']
            embed.add_field(name='> ' + str(i + 1), value=value)
        await ctx.channel.send(embed=embed)

        def check(m):
            if 1 <= int(m.content) <= len(chrIdList):
                return True
            else:
                return False
        try:
            msg = await bot.wait_for('message', check=check, timeout=15)
        except asyncio.TimeoutError:
            await ctx.channel.send('시간 끝! 더 고민해보고 다시 불러주세요.')
        else:
            server, chrId = chrIdList[int(msg.content) - 1]['server'], chrIdList[int(msg.content) - 1]['characterId']
    else:
        try:
            server, chrId = chrIdList[0]['server'], chrIdList[0]['characterId']
        except:
            await ctx.channel.send('해당 캐릭터를 찾을 수 없어요. 다시 한번 확인해주세요!')
            return

    chrEquipItemList, chrEquipItemEnchantInfo = DNFAPI.getChrEquipItemInfoList(server, chrId)
    chrEquipSetItemInfo = DNFAPI.getChrEquipSetItemInfo(chrEquipItemList)

    chrEquipSetItemName = []
    for i in chrEquipSetItemInfo:
        if i[2] is not None:
            chrEquipSetItemName.append(i[2])
    chrEquipSetItemName = list(set(chrEquipSetItemName))

    # embed 설정
    embed = discord.Embed(title=name + '님의 캐릭터 정보를 알려드릴게요.')
    embed.set_image(url='https://img-api.neople.co.kr/df/servers/' + DNFAPI.getServerId(server) + '/characters/' + chrId + '?zoom=1')

    # 필드 추가
    value = ''
    for i in chrEquipSetItemName:
        value += i + '\r\n'
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
    await ctx.channel.purge(limit=2)

    try:
        await ctx.channel.send(embed=embed)
    except:
        await ctx.channel.send('오류가 발생했어요... 다시 시도해주세요!')

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

    # 아이템 id 얻어오기 #
    itemId = 0
    itemIdList     = DNFAPI.getItemId(name)
    if not len(itemIdList):
        await ctx.channel.send('해당 장비를 찾을 수 없어요...\r\n장비 이름을 확인하고 다시 불러주세요!')
        return

    await ctx.channel.purge(limit=1)
    if len(itemIdList) >= 2:
        embed = discord.Embed(title='알고싶은 장비 아이템의 번호를 입력해주세요!', description='10초만 기다려드릴거에요. 빠르게 골라주세요!')
        for i in range(len(itemIdList)):
            embed.add_field(name='> ' + str(i + 1), value=itemIdList[i]['itemName'])
        await ctx.channel.send(embed=embed)

        def check(m):
            if 1 <= int(m.content) <= len(itemIdList):
                return True
            else:
                return False
        try:
            msg = await bot.wait_for('message', check=check, timeout=10)
        except asyncio.TimeoutError:
            await ctx.channel.send('시간 끝! 더 고민해보고 다시 불러주세요.')
        else:
            itemId = itemIdList[int(msg.content) - 1]['itemId']
    else:
        itemId = itemIdList[0]['itemId']

    ######################

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

    await ctx.channel.purge(limit=2)
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

    await ctx.channel.purge(limit=1)
    setItemIdList = DNFAPI.getSetItemIdList(setItemName)
    setItemId = -1

    if not len(setItemIdList):
        await ctx.channel.send('해당 세트를 찾을 수 없어요...\r\n세트 이름을 확인하고 다시 불러주세요!')
        return

    if len(setItemIdList) >= 2:
        embed = discord.Embed(title='알고싶은 세트옵션의 번호를 입력해주세요!', description='10초만 기다려드릴거에요. 빠르게 골라주세요!')
        for i in range(len(setItemIdList)):
            embed.add_field(name='> ' + str(i + 1), value=setItemIdList[i]['setItemName'])
        await ctx.channel.send(embed=embed)

        def check(m):
            if 1 <= int(m.content) <= len(setItemIdList):
                return True
            else:
                return False
        try:
            msg = await bot.wait_for('message', check=check, timeout=10)
        except asyncio.TimeoutError:
            await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요!')
        else:
            setItemId, setItemName = setItemIdList[int(msg.content) - 1]['setItemId'], setItemIdList[int(msg.content) - 1]['setItemName']
    else:
        setItemId, setItemName = setItemIdList[0]['setItemId'], setItemIdList[0]['setItemName']

    setItemInfoList, setItemOptionList = DNFAPI.getSetItemInfoList(setItemId)
    embed2 = discord.Embed(title=setItemName + '의 정보를 알려드릴게요.')
    for i in setItemInfoList:
        embed2.add_field(name='> ' + i['itemRarity'] + ' ' + i['slotName'], value=i['itemName'] + '\r\n')
    for i in setItemOptionList:
        embed2.add_field(name='> ' + str(i['optionNo']) + '세트 옵션', value=i['explain'])
    itemImageUrl = DNFAPI.getItemImageUrl(setItemInfoList[0]['itemId'])
    embed2.set_thumbnail(url=itemImageUrl)

    await ctx.channel.purge(limit=2)
    await ctx.channel.send(embed=embed2)

bot.remove_command('help')
bot.run(token)
