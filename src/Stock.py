import json
import discord
import asyncio
from src import DNFAPI, Util
from datetime import datetime
from database import Connection, Tool

async def 출석(ctx):
    await ctx.message.delete()
    did, name = str(ctx.message.author.id), ctx.message.author.display_name
    waiting = await ctx.channel.send(f'> {name}님의 출석을 확인하고있어요...')

    # 출석 체크 확인
    dailyCheck = Tool.getDailyCheck(did)
    today = datetime.now().strftime('%Y-%m-%d')
    if dailyCheck is not None and str(dailyCheck.get('date')) == today:
        embed = discord.Embed(title=f'{name}님의 출석체크')
        embed.add_field(name='> 출석 날짜', value=today)
        embed.add_field(name='> 출석 일수', value=f"{dailyCheck['count']}일")
        embed.add_field(name='> 출석 보상', value='X')
        embed.set_footer(text='이미 출석체크를 했어요.')
        await waiting.delete()
        await ctx.channel.send(embed=embed)
        return

    # 출석 체크
    if Tool.getAccount(did) is None:
        Tool.iniAccount(did)
    reward = Util.getDailyReward()
    Tool.gainGold(did, reward)
    Tool.updateDailyCheck(did)
    dailyCheck = Tool.getDailyCheck(did)

    embed = discord.Embed(title=f'{name}님의 출석체크')
    embed.add_field(name='> 출석 날짜', value=today)
    embed.add_field(name='> 출석 일수', value=f"{dailyCheck['count']}일")
    embed.add_field(name='> 출석 보상', value=format(reward, ',') + '골드')
    embed.set_footer(text='출석체크 완료!')
    await waiting.delete()
    await ctx.channel.send(embed=embed)

async def 주식(ctx):
    await ctx.message.delete()
    did, name = ctx.message.author.id, ctx.message.author.display_name
    waiting = await ctx.channel.send(f'> {name}님의 주식 정보를 불러오고 있어요...')

    stock = Tool.getStock(did)
    if stock is None:
        Tool.iniStock(did)
        stock = Tool.getStock(did)
    holding = json.loads(stock['holding'])

    # 주가 최신화
    newPrice = []
    for i in holding.values():
        if i is None: break
        auction = DNFAPI.getItemAuctionPrice(i['name'])
        _, price = Util.updateAuctionData(i['name'], auction)
        newPrice.append(price['평균가'])

    # 계산
    money = format(Tool.getGold(did), ',') + '골드'
    totBid = getTotBit(stock)
    totGain = getTotGain(stock, newPrice)
    totProfit = getTotProfit(totBid, totGain)

    # 결과
    embed = discord.Embed(title=ctx.message.author.display_name + '님의 주식 정보를 알려드릴게요.')
    embed.add_field(name='> 보유 금액', value=money, inline=False)
    embed.add_field(name='> 총 수익률', value=totProfit)
    embed.add_field(name='> 총 매수금', value=format(totBid, ',') + '골드')
    embed.add_field(name='> 총 평가금', value=format(totGain, ',') + '골드')

    for i in range(3):
        try:
            h = holding[str(i + 1)]
            name = '> ' + h['name']
            value = '현재 단가 : ' + format(newPrice[i], ',') + '골드\r\n'
            value += '매수 단가 : ' + format(h['bid'], ',') + '골드\r\n'
            value += '매수량 : ' + format(h['count'], ',') + '개\r\n'
            value += '수익률 : ' + Util.getVolatility(h['bid'], newPrice[i])
        except:
            name = '> 종목' + str(i + 1)
            value = '보유 중인 주식이 없습니다.'
        embed.add_field(name=name, value=value)
    await waiting.delete()
    await ctx.channel.send(embed=embed)

async def 매수(bot, ctx, *input):
    await ctx.message.delete()
    if not input:
        await ctx.channel.send("> !주식매수 '아이템이름' 의 형태로 적어야해요!")
        return

    waiting = await ctx.channel.send('> 해당 주식의 정보를 불러오는 중입니다...')
    name = DNFAPI.getMostSimilarItemName(Util.mergeString(*input))
    if '카드' in name:
        text = '> 현재 카드는 매수할 수 없어요.\r\n'
        text += '> 카드도 매수할 수 있도록 노력해볼게요!'
        await waiting.delete()
        await ctx.channel.send(text)
        return

    auction = DNFAPI.getItemAuctionPrice(name)
    if not auction:
        await waiting.delete()
        await ctx.channel.send('> 해당 아이템의 판매 정보를 얻어오지 못했어요.')
        return

    prev, price = Util.updateAuctionData(name, auction)
    embed = discord.Embed(title=ctx.message.author.display_name + '님의 매수 주문',
                          description='매수하려면 O, 취소하려면 X 이모지를 입력해주세요.')
    embed.add_field(name='> 단가',        value=format(price['평균가'], ',') + '골드')
    embed.add_field(name='> 최근 판매량', value=format(price['판매량'], ',') + '개')
    embed.add_field(name='> 가격 변동률', value=Util.getVolatility(prev, price['평균가'])) + ' (' + prev['date'].strftime('%Y-%m-%d') + ')'
    embed.set_footer(text='30초 안에 결정해야합니다.')
    embed.set_thumbnail(url=DNFAPI.getItemImageUrl(auction[0]['itemId']))
    await waiting.delete()
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('⭕')
    await msg.add_reaction('❌')

    try:
        def check(_reaction, _user):
            return (str(_reaction) == '⭕' or str(_reaction) == '❌') \
                   and _user == ctx.author and _reaction.message.id == msg.id
        reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)
        if str(reaction) == '⭕':
            await msg.delete()
            await buyStock(bot, ctx, name, price)
        elif str(reaction) == '❌':
            await msg.delete()
            await ctx.channel.send('> 매수가 취소되었습니다.')
    except asyncio.TimeoutError:
        await msg.delete()
        await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
    except Exception as e:
        await ctx.channel.send('> 오류가 발생했어요.\r\n> ' + str(e))

async def 매도(bot, ctx):
    await ctx.message.delete()
    did, name = ctx.message.author.id, ctx.message.author.display_name
    waiting = await ctx.channel.send(f'> {name}님의 보유 주식을 불러오는 중입니다...')

    stock = Tool.getStock(did)
    holding = json.loads(stock['holding'])
    if getHoldingCount(holding) == 0:
        text = f'> {name}님은 매도할 주식이 없어요.\r\n'
        text += '> `!주식매수` 명령어를 사용해서 주식을 매수해보세요!'
        await waiting.delete()
        await ctx.channel.send(text)
        return

    newPrice = []
    embed = discord.Embed(title='판매할 종목을 선택해주세요.')
    for i in holding.values():
        if i is None: break
        auction = DNFAPI.getItemAuctionPrice(i['name'])
        _, price = Util.updateAuctionData(i['name'], auction)
        newPrice.append(price['평균가'])

        value = '매도 단가 : '  + format(price['평균가'], ',') + '\r\n'
        value += '매수 단가 : ' + format(i['bid'], ',') + '\r\n'
        value += '보유량 : '    + format(i['count'], ',')
        embed.add_field(name='> ' + i['name'], value=value)
    embed.set_footer(text='30초 안에 결정해야합니다.')
    await waiting.delete()
    msg = await ctx.channel.send(embed=embed)

    if getHoldingCount(holding) >= 1: await msg.add_reaction('1️⃣')
    if getHoldingCount(holding) >= 2: await msg.add_reaction('2️⃣')
    if getHoldingCount(holding) >= 3: await msg.add_reaction('3️⃣')

    try:
        def check(_reaction, _user):
            return str(_reaction) in ['1️⃣', '2️⃣', '3️⃣'] and _user == ctx.author and _reaction.message.id == msg.id
        reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)

        if str(reaction) == '1️⃣' and getHoldingCount(holding) >= 1:
            await msg.delete()
            await sellStock(bot, ctx, holding, 1, newPrice[0])
        elif str(reaction) == '2️⃣' and getHoldingCount(holding) >= 2:
            await msg.delete()
            await sellStock(bot, ctx, holding, 2, newPrice[1])
        elif str(reaction) == '3️⃣' and getHoldingCount(holding) >= 3:
            await msg.delete()
            await sellStock(bot, ctx, holding, 3, newPrice[2])
    except asyncio.TimeoutError:
        await msg.delete()
        await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
    except Exception as e:
        await ctx.channel.send('> 오류가 발생했어요.\r\n> ' + str(e))

async def 주식랭킹(bot, ctx):
    await ctx.message.delete()
    waiting = await ctx.channel.send('> 주식 랭킹을 불러오는 중이예요...')

    stocks = Tool.getStock()
    auction = Tool.getAuction()
    rank = getSortedStockRank(stocks, auction)

    if not rank:
        embed = discord.Embed(title='주식 랭킹을 알려드릴게요!',
                              description='> 랭킹 데이터가 없어요. `!주식매수` 명령어를 사용해서 매수해보세요!')
        await waiting.delete()
        await ctx.channel.send(embed=embed)
        return

    page = 0
    embed = getStockRankEmbed(ctx, rank, auction, page)
    embed.set_footer(text=f'{(len(rank) - 1) // 15 + 1}쪽 중 1쪽')
    await waiting.delete()
    msg = await ctx.channel.send(embed=embed)

    if len(rank) > 15:
        await msg.add_reaction('▶️')
    while len(rank) > 15:
        try:
            def check(_reaction, _user):
                return str(_reaction) in ['◀️', '▶️'] and _user == ctx.author and _reaction.message.id == msg.id
            reaction, user = await bot.wait_for('reaction_add', check=check)

            if str(reaction) == '◀️' and page > 0:
                page -= 1
            if str(reaction) == '▶️' and page < (len(rank) - 1) // 15:
                page += 1

            embed = getStockRankEmbed(ctx, rank, auction, page)
            embed.set_footer(text=f'{(len(rank) - 1) // 15 + 1}쪽 중 {page + 1}쪽')
            await msg.edit(embed=embed)
            await msg.clear_reactions()

            if page > 0:
                await msg.add_reaction('◀️')
            if page < (len(rank) - 1) // 15:
                await msg.add_reaction('▶️')
        except: pass

async def buyStock(bot, ctx, name, price):
    did = ctx.message.author.id

    # 계좌가 없을 경우 생성
    gold, stock = Tool.getGold(did), Tool.getStock(did)
    if gold is None:
        Tool.iniAccount(did)
        gold = Tool.getGold(did)
    holding = json.loads(stock['holding'])

    # 추가 매수하는 경우
    isOverride = False
    for i in holding.values():
        if i is not None and i['name'] == name:
            isOverride = True
            break

    if getHoldingCount(holding) >= 3 and not isOverride:
        embed = discord.Embed(title=ctx.message.author.display_name + '님의 매수 주문',
                              description='최대 3가지 종목만 보유할 수 있어요. `!주식매도` 명령어를 사용해서 보유한 주식을 매도할 수 있어요.')
        await ctx.channel.send(embed=embed)
        return

    embed = discord.Embed(title=ctx.message.author.display_name + '님의 매수 주문',
                          description=name + '을(를) 매수하실 양을 입력해주세요.')
    embed.add_field(name='> 보유 금액', value=format(gold, ',') + '골드')
    embed.add_field(name='> 매수 단가', value=format(price['평균가'], ',') + '골드')
    embed.add_field(name='> 매수 가능 갯수', value=format(gold // price['평균가'], ',') + '개')
    embed.set_footer(text='30초 안에 결정해야합니다.')
    msg = await ctx.channel.send(embed=embed)

    try:
        def check(m):
            return ctx.channel.id == m.channel.id and ctx.message.author == m.author
        result = await bot.wait_for('message', check=check, timeout=30)
        bid, count = price['평균가'], int(result.content)

        # 예외처리
        if count <= 0:
            embed2 = discord.Embed(title=ctx.message.author.display_name + '님의 매수 주문',
                                   description='매수 갯수는 0 이하가 될 수 없어요. 다시 시도해주세요.')
            await result.delete()
            await msg.edit(embed=embed2)
            return
        if count >= gold // price['평균가']:
            embed2 = discord.Embed(title=ctx.message.author.display_name + '님의 매수 주문',
                                   description='매수 가능한 최대 갯수를 초과했어요. 다시 시도해주세요.')
            await result.delete()
            await msg.edit(embed=embed2)
            return

        # 추가 매수
        if isOverride:
            for i in holding.values():
                if i['name'] == name:
                    newCount = count + i['count']
                    newBid   = ((bid * count) + (i['bid'] * i['count'])) // newCount
                    i['count'], i['bid'] = newCount, newBid
                    break
        else:
            for k, v in holding.items():
                if v is None:
                    v = {
                        'name': name,
                        'bid': bid,
                        'count': count
                    }
                    holding[k] = v
                    break

        try:
            Tool.gainGold(did, -count * price['평균가'])

            conn, cur = Connection.getConnection()
            sql = 'UPDATE stock SET holding=%s WHERE did=%s'
            cur.execute(sql, (json.dumps(holding, ensure_ascii=False), did))
            conn.commit()
        except Exception as e:
            await ctx.channel.send(f'> 매수에 실패했어요.\r\n> {e}')
            return

        await result.delete()
        embed2 = discord.Embed(title=ctx.message.author.display_name + '님의 매수 주문',
                               description=name + '을(를) 성공적으로 매수했습니다.')
        embed2.add_field(name='> 매수 단가', value=format(bid, ',') + '골드')
        embed2.add_field(name='> 매수량',    value=format(count, ',') + '개')
        embed2.add_field(name='> 매수금',    value=format(count * bid, ',') + '골드')
        await msg.edit(embed=embed2)
    except asyncio.TimeoutError:
        await msg.delete()
        await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
    except Exception as e:
        await msg.delete()
        await result.delete()
        await ctx.channel.send('> 입력이 잘못되었어요. 다시 시도해주세요.')

async def sellStock(bot, ctx, holding, index, offer):
    did = ctx.message.author.id
    embed = discord.Embed(title=ctx.message.author.display_name + '님의 매도 주문',
                          description='매도할 양을 입력해주세요.\r\n매도 채결 시 1%의 수수료가 발생해요.')
    embed.add_field(name='> 종목', value=holding[str(index)]['name'])
    embed.add_field(name='> 매도 단가', value=format(offer, ',') + '골드')
    embed.add_field(name='> 매도 가능 갯수', value=format(holding[str(index)]['count'], ',') + '개')
    embed.set_footer(text='30초 안에 결정해야합니다.')
    msg = await ctx.channel.send(embed=embed)

    try:
        def check(m):
            return ctx.channel.id == m.channel.id and ctx.message.author == m.author
        result = await bot.wait_for('message', check=check, timeout=30)
        count = int(result.content)
        
        # 예외처리
        if count <= 0:
            await result.delete()
            embed2 = discord.Embed(title=ctx.message.author.display_name + '님의 매도 주문',
                                   description='매도 갯수는 0 이하가 될 수 없어요. 다시 시도해주세요.')
            await msg.edit(embed=embed2)
            return
        if count > holding[str(index)]['count']:
            await result.delete()
            embed2 = discord.Embed(title=ctx.message.author.display_name + '님의 매도 주문',
                                   description='매도 가능한 최대 갯수를 초과했습니다. 다시 시도해주세요.')
            await msg.edit(embed=embed2)
            return

        # 처리
        name = holding[str(index)]['name']
        holding[str(index)]['count'] -= count
        if holding[str(index)]['count'] <= 0:
            del holding[str(index)]
            for i in range(index, 3):
                try:
                    holding[str(i)] = holding[str(i + 1)]
                except: pass
            holding['3'] = None

        try:
            Tool.gainGold(did, int(offer * count * 0.99))
    
            conn, cur = Connection.getConnection()
            sql = 'UPDATE stock SET holding=%s WHERE did=%s'
            cur.execute(sql, (json.dumps(holding, ensure_ascii=False), did))
            conn.commit()
        except Exception as e:
            await ctx.channel.send(f'> 매도에 실패했어요.\r\n> {e}')
            return

        await result.delete()
        embed2 = discord.Embed(title=ctx.message.author.display_name + '님의 매도 주문',
                               description=name + '을(를) 성공적으로 매도했습니다.')
        embed2.add_field(name='> 매도 단가', value=format(offer, ',') + '골드')
        embed2.add_field(name='> 매도량', value=format(count, ',') + '개')
        embed2.add_field(name='> 매도금', value=format(int(count * offer * 0.99), ',') + '골드')
        await msg.edit(embed=embed2)
    except asyncio.TimeoutError:
        await msg.delete()
        await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
    except Exception as e:
        await msg.delete()
        await result.delete()
        await ctx.channel.send('> 입력이 잘못되었어요. 다시 시도해주세요.')
        print(e)

def getSortedStockRank(stocks, auction):
    def key(x):
        value = Tool.getGold(x['did'])
        for i in json.loads(x['holding']).values():
            value += getRecentPrice(auction, i['name']) * i['count']
        return value
    return sorted(stocks, key=lambda x: key(x), reverse=True)

def getStockRankEmbed(ctx, rank, auction, page):
    rank = rank[page * 15:page * 15 + 15]

    embed = discord.Embed(title='주식 랭킹을 알려드릴게요!',
                          description='현재 어떤 주식을 보유중인지도 알려드려요.')
    for index, i in enumerate(rank):
        name = f'> {page * 15 + index + 1}등'
        if i['did'] == str(ctx.message.author.id):
            name += f'({ctx.message.author.display_name}님)'

        # value 계산
        holdings = ''
        gold = Tool.getGold(i['did'])
        for _index, j in enumerate(json.loads(i['holding']).values()):
            try:
                holdings += f"종목{_index + 1} : {j['name']}\r\n"
                gold += getRecentPrice(auction, j['name']) * j['count']
            except: pass
        value = f'{format(gold, ",")}골드\r\n{holdings}'
        embed.add_field(name=name, value=value)
    return embed

def getRecentPrice(auction, name):
    for i in auction:
        if i['name'] == name:
            return i['price']
    return None

def getTotProfit(totBid, totGain):
    try:
        totProfit = (totGain / totBid - 1) * 100
        totProfit = float(format(totProfit, '.2f'))
        return makePlusMinus(totProfit)
    except:
        return '- 0.00%'

def getTotBit(stock):
    totBit = 0
    holding = json.loads(stock['holding'])
    for i in holding.values():
        try:
            totBit += i['bid'] * i['count']
        except: pass
    return totBit

def getTotGain(stock, newPrice):
    totGain = 0
    holding = json.loads(stock['holding'])
    for i in range(len(holding)):
        try:
            totGain += newPrice[i] * stock['holdings'][i]['count']
        except: pass
    return totGain

def makePlusMinus(num):
    if num >= 0:
        num = '▲ ' + format(num, ',') + '%'
    elif num == 0:
        num = '- 0.00%'
    else:
        num = '▼ ' + format(num, ',') + '%'
    return num

def getHoldingCount(holding):
    count = 0
    for i in holding.values():
        if i is not None:
            count += 1
    return count