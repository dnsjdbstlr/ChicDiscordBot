import discord
import re
from Src import Util, DNFAPI

async def 버프력(bot, ctx, *input):
    if not input:
        await ctx.message.delete()
        await ctx.channel.send('> !버프력 <닉네임> 또는 !캐릭터 <서버> <닉네임> 의 형태로 적어야해요!')
        return

    if len(input) == 2:
        server = input[0]
        name   = input[1]
    else:
        server = '전체'
        name   = input[0]

    try:
        chrIdList = DNFAPI.getChrIdList(server, name)
        server, chrId, name = await Util.getSelectionFromChrIdList(bot, ctx, chrIdList)
    except Exception as e:
        await ctx.message.delete()
        await ctx.channel.send(f'> 캐릭터 정보를 가져오는데 오류가 발생했어요.\r\n> {e}')
        return False

    # 아이템 옵션 계산
    equip     = DNFAPI.getChrEquipItems(server, chrId)
    avatar    = DNFAPI.getChrEquipAvatar(server, chrId)
    creature  = DNFAPI.getChrEquipCreature(server, chrId)
    allItemOptions = getAllItemOptions(equip, avatar)

    bEquip     = DNFAPI.getChrBuffEquip(server, chrId)
    bAvatar    = DNFAPI.getChrBuffAvatar(server, chrId)
    bCreature  = DNFAPI.getChrBuffCreature(server, chrId)
    bAllItemOptions = getAllItemOptions(bEquip, bAvatar, buff=True)

    # 스탯 계산
    status = { '힘': 0, '지능': 0, '체력': 0, '정신력': 0 }
    statInfo  = DNFAPI.getChrStatInfo(server, chrId)
    for i in statInfo['status']:
        if i['itemName'] in ['힘', '지능', '체력', '정신력']:
            status[i['itemName']] += i['value']

    incStatus = getStatusFromEquipAndAvatar(equip, avatar, creature['creature']['itemId'])
    bIncStatus = getStatusFromEquipAndAvatar(bEquip['skill']['buff'], bAvatar['skill']['buff'], bCreature['skill']['buff']['creature'][0]['itemId'])

    incStatus['지능']  += getPerpetierStat(allItemOptions)
    bIncStatus['지능'] += getPerpetierStat(bAllItemOptions)

    bStatus = {'힘'     : status['힘']     + bIncStatus['힘']     - incStatus['힘'],
               '지능'   : status['지능']   + bIncStatus['지능']   - incStatus['지능'],
               '체력'   : status['체력']   + bIncStatus['체력']   - incStatus['체력'],
               '정신력' : status['정신력'] + bIncStatus['정신력'] - incStatus['정신력'] }

    print(chrId)

def getAllItemOptions(equip, avatar, buff=False):
    # 모든 옵션은 여기에 저장
    allItemOptions = { 'NORM': [], 'BUFF': [], 'AVATAR': [] }

    # 스위칭 장비일 경우
    if buff:
        equip['equipment'] = equip['skill']['buff']['equipment']
        avatar['avatar'] = avatar['skill']['buff']['avatar']

    # 아이템효과
    itemIds = [i['itemId'] for i in equip['equipment']]
    itemDetails = DNFAPI.getItemsDetail(','.join(itemIds))

    # 칭호 제외 아이템 목록
    itemIds_Except_title = []

    for i in equip['equipment']:
        if i['slotName'] != '칭호':
            itemIds_Except_title.append(i['itemId'])

    # 활성화세트
    activeSet = {}
    for i in DNFAPI.getEquipActiveSet(','.join(itemIds_Except_title))['setItemInfo']:
        activeSet.update({i['setItemId']: i['activeSetNo']})

    # 세트템효과
    setItemDetails = DNFAPI.getSetItemsInfo(','.join(activeSet.keys()))

    # ----------------------------------

    # 기본 옵션, 버퍼 옵션
    for itemDetail in itemDetails:
        # 기본 옵션
        if itemDetail.get('itemExplain') is not None:
            temp = itemDetail['itemExplain'].replace('\n\n', ', ')
            temp = temp.replace('\n', ', ')
            allItemOptions['NORM'].append(temp)

        # 버퍼 옵션
        if itemDetail.get('itemBuff') is not None:
            # 옵션
            temp = itemDetail['itemBuff']['explain'].replace('\n\n', ', ')
            temp = temp.replace('\n', ', ')
            allItemOptions['BUFF'].append(temp)

            # 스킬 레벨 증가
            reinforceSkill = itemDetail['itemBuff']['reinforceSkill']
            for skill in reinforceSkill:
                for info in skill['skills']:
                    text = f"{info['itemName']} 스킬Lv +{info['value']}"
                    allItemOptions['BUFF'].append(text)

    # 세트 옵션
    for k, v in activeSet.items():
        for setItemDetail in setItemDetails:
            if k == setItemDetail['setItemId']:
                for option in setItemDetail['setItemOption']:
                    if option['optionNo'] <= v:
                        # 옵션
                        if option.get('explain') is not None:
                            allItemOptions['NORM'].append(option['explain'])

                        # 버퍼 옵션
                        if option.get('itemBuff') is not None:
                            # 옵션
                            temp = option['itemBuff']['explain'].replace('\n\n', ', ')
                            temp = temp.replace('\n', ', ')
                            allItemOptions['BUFF'].append(temp)

                            # 스킬 레벨 증가
                            incSkillLevel = getSkillLevelingInfo(option['itemBuff']['reinforceSkill'])
                            for _k, _v in incSkillLevel.items():
                                for inc in incSkillLevel[_k]:
                                    allItemOptions['BUFF'].append(inc)

    # 칭호, 연옥, 신화 옵션
    for itemDetail in equip['equipment']:
        # 칭호 옵션
        if itemDetail['slotName'] == '칭호':
            try:
                # 스킬 레벨 증가
                incSkillLevel = getSkillLevelingInfo(itemDetail['enchant']['reinforceSkill'])
                for _k, _v in incSkillLevel.items():
                    for inc in incSkillLevel[_k]:
                        allItemOptions['BUFF'].append(inc)
            except:
                pass

        # 연옥 옵션
        if itemDetail.get('transformInfo') is not None:
            # 옵션
            temp = itemDetail['transformInfo']['explain'].replace('\n\n', ', ')
            temp = temp.replace('\n', ', ')
            allItemOptions['NORM'].append(temp)

            # 버퍼 옵션
            temp = itemDetail['transformInfo']['buffExplain'].replace('\n\n', ', ')
            temp = temp.replace('\n', ', ')
            allItemOptions['BUFF'].append(temp)

    # 시로코 옵션
    sirocoInfo = getSirocoItemInfo(equip)
    if sirocoInfo is not None:
        # 1옵션
        for v in sirocoInfo.values():
            try:
                allItemOptions['NORM'].append(v['NORM']['1옵션'])
                allItemOptions['BUFF'].append(v['BUFF']['1옵션'])
            except: pass

        # 2옵션
        # 잔향
        try:
            if 3 in sirocoInfo['세트'].values():
                allItemOptions['NORM'].append(sirocoInfo['잔향']['NORM']['2옵션'])
                allItemOptions['BUFF'].append(sirocoInfo['잔향']['BUFF']['2옵션'])
        except: pass

        # 넥스
        if '무형 : 넥스의 잠식된 의복' in sirocoInfo.keys() and '무의식 : 넥스의 몽환의 어둠' in sirocoInfo.keys():
            allItemOptions['NORM'].append(sirocoInfo['무형 : 넥스의 잠식된 의복']['NORM']['2옵션'])
            allItemOptions['BUFF'].append(sirocoInfo['무형 : 넥스의 잠식된 의복']['BUFF']['2옵션'])
        if '무의식 : 넥스의 몽환의 어둠' in sirocoInfo.keys() and '환영 : 넥스의 검은 기운' in sirocoInfo.keys():
            allItemOptions['NORM'].append(sirocoInfo['무의식 : 넥스의 몽환의 어둠']['NORM']['2옵션'])
            allItemOptions['BUFF'].append(sirocoInfo['무의식 : 넥스의 몽환의 어둠']['BUFF']['2옵션'])
        if '환영 : 넥스의 검은 기운' in sirocoInfo.keys() and '무형 : 넥스의 잠식된 의복' in sirocoInfo.keys():
            allItemOptions['NORM'].append(sirocoInfo['환영 : 넥스의 검은 기운']['NORM']['2옵션'])
            allItemOptions['BUFF'].append(sirocoInfo['환영 : 넥스의 검은 기운']['BUFF']['2옵션'])

        # 암살
        if '무형 : 암살자의 잠식된 의식' in sirocoInfo.keys() and '무의식 : 암살자의 몽환의 흔적' in sirocoInfo.keys():
            allItemOptions['NORM'].append(sirocoInfo['무형 : 암살자의 잠식된 의식']['NORM']['2옵션'])
            allItemOptions['BUFF'].append(sirocoInfo['무형 : 암살자의 잠식된 의식']['BUFF']['2옵션'])
        if '무의식 : 암살자의 몽환의 흔적' in sirocoInfo.keys() and '환영 : 암살자의 검은 검집' in sirocoInfo.keys():
            allItemOptions['NORM'].append(sirocoInfo['무의식 : 암살자의 몽환의 흔적']['NORM']['2옵션'])
            allItemOptions['BUFF'].append(sirocoInfo['무의식 : 암살자의 몽환의 흔적']['BUFF']['2옵션'])
        if '환영 : 암살자의 검은 검집' in sirocoInfo.keys() and '무형 : 암살자의 잠식된 의식' in sirocoInfo.keys():
            allItemOptions['NORM'].append(sirocoInfo['환영 : 암살자의 검은 검집']['NORM']['2옵션'])
            allItemOptions['BUFF'].append(sirocoInfo['환영 : 암살자의 검은 검집']['BUFF']['2옵션'])

        # 록시
        if '무형 : 록시의 잠식된 광기' in sirocoInfo.keys() and '무의식 : 록시의 몽환의 약속' in sirocoInfo.keys():
            allItemOptions['NORM'].append(sirocoInfo['무형 : 록시의 잠식된 광기']['NORM']['2옵션'])
            allItemOptions['BUFF'].append(sirocoInfo['무형 : 록시의 잠식된 광기']['BUFF']['2옵션'])
        if '무의식 : 록시의 몽환의 약속' in sirocoInfo.keys() and '환영 : 록시의 검은 구속구' in sirocoInfo.keys():
            allItemOptions['NORM'].append(sirocoInfo['무의식 : 록시의 몽환의 약속']['NORM']['2옵션'])
            allItemOptions['BUFF'].append(sirocoInfo['무의식 : 록시의 몽환의 약속']['BUFF']['2옵션'])
        if '환영 : 록시의 검은 구속구' in sirocoInfo.keys() and '무형 : 록시의 잠식된 광기' in sirocoInfo.keys():
            allItemOptions['NORM'].append(sirocoInfo['환영 : 록시의 검은 구속구']['NORM']['2옵션'])
            allItemOptions['BUFF'].append(sirocoInfo['환영 : 록시의 검은 구속구']['BUFF']['2옵션'])

        # 수문장
        if '무형 : 수문장의 잠식된 갑주' in sirocoInfo.keys() and '무의식 : 수문장의 몽환의 사념' in sirocoInfo.keys():
            allItemOptions['NORM'].append(sirocoInfo['무형 : 수문장의 잠식된 갑주']['NORM']['2옵션'])
            allItemOptions['BUFF'].append(sirocoInfo['무형 : 수문장의 잠식된 갑주']['BUFF']['2옵션'])
        if '무의식 : 수문장의 몽환의 사념' in sirocoInfo.keys() and '환영 : 수문장의 검은 가면' in sirocoInfo.keys():
            allItemOptions['NORM'].append(sirocoInfo['무의식 : 수문장의 몽환의 사념']['NORM']['2옵션'])
            allItemOptions['BUFF'].append(sirocoInfo['무의식 : 수문장의 몽환의 사념']['BUFF']['2옵션'])
        if '환영 : 수문장의 검은 가면' in sirocoInfo.keys() and '무형 : 수문장의 잠식된 갑주' in sirocoInfo.keys():
            allItemOptions['NORM'].append(sirocoInfo['환영 : 수문장의 검은 가면']['NORM']['2옵션'])
            allItemOptions['BUFF'].append(sirocoInfo['환영 : 수문장의 검은 가면']['BUFF']['2옵션'])

        # 로도스
        if '무형 : 로도스의 잠식된 의지' in sirocoInfo.keys() and '무의식 : 로도스의 몽환의 근원' in sirocoInfo.keys():
            allItemOptions['NORM'].append(sirocoInfo['무형 : 로도스의 잠식된 의지']['NORM']['2옵션'])
            allItemOptions['BUFF'].append(sirocoInfo['무형 : 로도스의 잠식된 의지']['BUFF']['2옵션'])
        if '무의식 : 로도스의 몽환의 근원' in sirocoInfo.keys() and '환영 : 로도스의 검은 핵' in sirocoInfo.keys():
            allItemOptions['NORM'].append(sirocoInfo['무의식 : 로도스의 몽환의 근원']['NORM']['2옵션'])
            allItemOptions['BUFF'].append(sirocoInfo['무의식 : 로도스의 몽환의 근원']['BUFF']['2옵션'])
        if '환영 : 로도스의 검은 핵' in sirocoInfo.keys() and '무형 : 로도스의 잠식된 의지' in sirocoInfo.keys():
            allItemOptions['NORM'].append(sirocoInfo['환영 : 로도스의 검은 핵']['NORM']['2옵션'])
            allItemOptions['BUFF'].append(sirocoInfo['환영 : 로도스의 검은 핵']['BUFF']['2옵션'])

    # 아바타 옵션
    for i in avatar['avatar']:
        if i['slotName'] == '상의 아바타':
            allItemOptions['AVATAR'].append(i['optionAbility'])
            break

    return allItemOptions

def getSirocoItemInfo(equip):
    # 결과
    sirocoInfo = {}

    # 잔향, 무형, 무의식, 환영
    reverberation = {'NORM' : {}, 'BUFF' : {}}
    intangible    = {'NORM' : {}, 'BUFF' : {}}
    unconscious   = {'NORM' : {}, 'BUFF' : {}}
    illusion      = {'NORM' : {}, 'BUFF' : {}}
    intangibleType, unconsciousType, illusionType = '', '', ''

    # 활성화 세트
    setCount = { '넥스': 0, '암살자': 0, '록시': 0, '수문장': 0, '로도스': 0 }

    for i in equip['equipment']:
        if i.get('sirocoInfo') is None: continue
        if i.get('upgradeInfo') is None: continue

        # 활성화 세트 계산
        for name in ['넥스', '암살자', '록시', '수문장', '로도스']:
            if name in i['upgradeInfo']['itemName']: setCount[name] += 1

        # 시로코 옵션 계산
        for idx, option in enumerate(i['sirocoInfo']['options']):
            norm = option['explain'].replace('\n\n', ' ')
            norm = norm.replace('\n', '')

            buff = option['buffExplain'].replace('\n\n', ' ')
            buff = buff.replace('\n', '')

            # 잔향
            if i['slotName'] == '무기':
                reverberation['NORM'].update({f"{idx+1}옵션" : norm})
                reverberation['BUFF'].update({f"{idx+1}옵션" : buff})

            # 무형
            if i['slotName'] == '하의':
                intangible['NORM'].update({f"{idx+1}옵션" : norm})
                intangible['BUFF'].update({f"{idx+1}옵션" : buff})
                intangibleType = i['upgradeInfo']['itemName']

            # 무의식
            elif i['slotName'] == '반지':
                unconscious['NORM'].update({f"{idx+1}옵션" : norm})
                unconscious['BUFF'].update({f"{idx+1}옵션" : buff})
                unconsciousType = i['upgradeInfo']['itemName']

            # 환영
            elif i['slotName'] == '보조장비':
                illusion['NORM'].update({f"{idx+1}옵션" : norm})
                illusion['BUFF'].update({f"{idx+1}옵션" : buff})
                illusionType = i['upgradeInfo']['itemName']

    sirocoInfo['세트'] = setCount
    if len(reverberation) != 0: sirocoInfo['잔향'] = reverberation
    if len(intangible)    != 0: sirocoInfo[intangibleType] = intangible
    if len(unconscious)   != 0: sirocoInfo[unconsciousType] = unconscious
    if len(illusion)      != 0: sirocoInfo[illusionType] = illusion

    if len(reverberation) == 0 and len(intangible) == 0 and len(unconscious) == 0 and len(illusion) == 0:
        return None
    else:
        return sirocoInfo

def getStatusFromEquipAndAvatar(equip, avatar, creatureItemId):
    incStatus    = {'힘': 0, '지능': 0, '체력': 0, '정신력': 0}
    equipItemIds = [i['itemId'] for i in equip['equipment']]
    itemStatuses = [i['itemStatus'] for i in DNFAPI.getItemsDetail(','.join(equipItemIds))]
    
    # 아이템 기본 옵션
    for i in itemStatuses:
        for j in i:
            if j['itemName'] in ['힘', '지능', '체력', '정신력']:
                incStatus[j['itemName']] += int(j['value'])

    # 마법부여, 증폭
    for i in equip['equipment']:
        if i.get('enchant') is not None and i['enchant'].get('status') is not None:
            for j in i['enchant']['status']:
                if j['itemName'] in ['힘', '지능', '체력', '정신력']:
                    incStatus[j['itemName']] += int(j['value'])

        if i['amplificationName'] is None: continue
        RE = re.compile('차원의 (?P<value>\S+)')
        SE = re.search(RE, i['amplificationName'])
        incStatus[SE.group('value')] += getAmplificationStat(i['itemRarity'], i['reinforce'])

    # 아바타
    for i in avatar['avatar']:
        if i['optionAbility'] == '지능 45 증가':
            incStatus['지능'] += 45
        if i['optionAbility'] == '지능 55 증가':
            incStatus['지능'] += 55
        for j in i['emblems']:
            if j['itemName'] == '찬란한 그린 엠블렘[지능]':
                incStatus['지능'] += 15
            if j['itemName'] == '찬란한 붉은빛 엠블렘[지능]':
                incStatus['지능'] += 25
            if j['itemName'] == '찬란한 듀얼 엠블렘[지능 + HP MAX]':
                incStatus['지능'] += 15

    # 크리쳐
    for i in DNFAPI.getItemDetail(creatureItemId)['itemStatus']:
        if i['itemName'] in ['힘', '지능', '체력', '정신력']:
            incStatus[i['itemName']] += int(i['value'])

    return incStatus

def getSkillLevelingInfo(reinforceSkill):
    result = {}
    for j in reinforceSkill:
        jobName = '모든 직업' if j['jobName'] == '공통' else j['jobName']

        # 레벨 범위+
        levelRange = j.get('levelRange')
        if levelRange is not None:
            for k in j['levelRange']:
                minLv, maxLv, value = k.values()
                text = str(minLv) + ' ~ ' + str(maxLv) + ' 레벨 모든 스킬 Lv +' + str(value)

                if result.get(jobName) is None:
                    result[jobName] = [text]
                else:
                    result[jobName].append(text)

        # 단순 스킬+
        skills = j.get('skills')
        if skills is not None:
            for k in skills:
                text = k['itemName'] + ' 스킬Lv +' + str(k['value'])

                if result.get(jobName) is None:
                    result[jobName] = [text]
                else:
                    result[jobName].append(text)
    return result

def getPerpetierStat(allItemOption):
    stat = 0
    _re = re.compile('퍼페티어 지능 (?P<value>\d+) 증가')
    for option in allItemOption['BUFF']:
        search = re.search(_re, option)
        if search is not None:
            stat += int(search.group('value'))
    return stat

def getAmplificationStat(itemRarity, reinforce):
    EPIC = {
        '0' : 12,
        '1' : 14,
        '2' : 16,
        '3' : 18,
        '4' : 20,
        '5' : 25,
        '6' : 29,
        '7' : 33,
        '8' : 60,
        '9' : 73,
        '10': 88,
        '11': 103,
        '12': 126,
        '13': 163
    }

    MYTH = {
        '0' : 13,
        '1' : 15,
        '2' : 17,
        '3' : 20,
        '4' : 22,
        '5' : 27,
        '6' : 31,
        '7' : 36,
        '8' : 64,
        '9' : 78,
        '10': 94,
        '11': 111,
        '12': 134,
        '13': 174
    }

    reinforce = min(13, reinforce)
    if itemRarity == '신화':
        return MYTH[str(reinforce)]
    else:
        return EPIC[str(reinforce)]
