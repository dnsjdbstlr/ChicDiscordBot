import json
import discord
import asyncio
from src import dnfAPI, util
from datetime import datetime
from database import connection, tool

async def 출석(ctx):
    await ctx.message.delete()
    did, name = str(ctx.message.author.id), ctx.message.author.display_name
    waiting = await ctx.channel.send(f'> {name}님의 출석을 확인하고있어요...')

    # 주식 정보 확인
    stock = tool.getStock(did)
    if stock is None:
        embed = discord.Embed(title=f'{name}님의 출석체크',
                              description='`!주식` 명령어를 사용한 후 다시 시도해주세요.')
        await waiting.delete()
        await ctx.channel.send(embed=embed)
        return

    # 출석 체크 확인
    dailyCheck = tool.getDailyCheck(did)
    today = datetime.now().strftime('%Y-%m-%d')
    if str(dailyCheck.get('date')) == today:
        embed = discord.Embed(title=f'{name}님의 출석체크')
        embed.add_field(name='> 출석 날짜', value=today)
        embed.add_field(name='> 출석 일수', value=f"{dailyCheck['count']}일")
        embed.add_field(name='> 출석 보상', value='X')
        embed.set_footer(text='이미 출석체크를 했어요.')
        await waiting.delete()
        await ctx.channel.send(embed=embed)
        return

    # 출석 체크
    reward = util.getDailyReward()
    tool.gainGold(did, reward)
    tool.updateDailyCheck(did)
    dailyCheck = tool.getDailyCheck(did)

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

    stock = tool.getStock(did)
    if stock is None:
        tool.iniStock(did)
        stock = tool.getStock(did)

    # 기존 코드와 호환
    stock['holdings'] = getHoldings(stock)

    # 주가 최신화
    newPrice = []
    for i in stock['holdings']:
        if i is None: break
        auction = dnfAPI.getItemAuctionPrice(i['name'])
        _, price = util.updateAuctionData(i['name'], auction)
        newPrice.append(price['평균가'])

    # 계산
    money = format(stock['gold'], ',') + '골드'
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
            holdings = stock['holdings'][i]
            name = '> ' + holdings['name']
            value = '현재 단가 : ' + format(newPrice[i], ',') + '골드\r\n'
            value += '매수 단가 : ' + format(holdings['bid'], ',') + '골드\r\n'
            value += '매수량 : ' + format(holdings['count'], ',') + '개\r\n'
            #value += '매수금 : ' + format(holdings['bid'] * holdings['count'], ',') + '골드\r\n'
            value += '수익률 : ' + util.getVolatility2(holdings['bid'], newPrice[i])
        except Exception as e:
            name = '> 종목' + str(i + 1)
            value = '보유 중인 주식이 없습니다.'
        embed.add_field(name=name, value=value)
    await waiting.delete()
    await ctx.channel.send(embed=embed)

async def 주식매수(bot, ctx, *input):
    await ctx.message.delete()

    if not input:
        await ctx.channel.send("> !주식매수 '아이템이름' 의 형태로 적어야해요!")
        return

    waiting = await ctx.channel.send('> 해당 주식의 정보를 불러오는 중입니다...')
    name = dnfAPI.getMostSimilarItemName(util.mergeString(*input))
    if '카드' in name:
        text = '> 현재 카드는 매수할 수 없어요.\r\n'
        text += '> 카드도 매수할 수 있도록 노력해볼게요!'
        await waiting.delete()
        await ctx.channel.send(text)
        return

    auction = dnfAPI.getItemAuctionPrice(name)
    if not auction:
        await waiting.delete()
        await ctx.channel.send('> 해당 아이템의 판매 정보를 얻어오지 못했어요.')
        return

    prev, price = util.updateAuctionData(name, auction)
    embed = discord.Embed(title=ctx.message.author.display_name + '님의 매수 주문',
                          description='매수하려면 O, 취소하려면 X 이모지를 입력해주세요.')
    embed.add_field(name='> 단가',        value=format(price['평균가'], ',') + '골드')
    embed.add_field(name='> 최근 판매량', value=format(price['판매량'], ',') + '개')
    embed.add_field(name='> 가격 변동률', value=util.getVolatility(prev, price['평균가']))
    embed.set_footer(text='30초 안에 결정해야합니다.')
    embed.set_thumbnail(url=dnfAPI.getItemImageUrl(auction[0]['itemId']))
    await waiting.delete()
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('⭕')
    await msg.add_reaction('❌')

    try:
        def check(reaction, user):
            return (str(reaction) == '⭕' or str(reaction) == '❌') \
                   and user == ctx.author and reaction.message.id == msg.id
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

async def 주식매도(bot, ctx):
    await ctx.message.delete()
    did, name = ctx.message.author.id, ctx.message.author.display_name
    waiting = await ctx.channel.send(f'> {name}님의 보유 주식을 불러오는 중입니다...')

    stock = tool.getStock(did)
    if stock is None:
        text = f'> {name}님의 주식 정보를 찾을 수 없어요.\r\n'
        text += '> `!주식` 명령어를 사용한 후 다시 입력해주세요.'
        await waiting.delete()
        await ctx.channel.send(text)
        return

    stock['holdings'] = getHoldings(stock)
    if len(stock['holdings']) == 0:
        text = f'> {name}님은 매도할 주식이 없어요.\r\n'
        text += '> `!주식매수` 명령어를 사용해서 주식을 매수해보세요!'
        await waiting.delete()
        await ctx.channel.send(text)
        return

    newPrice = []
    embed = discord.Embed(title='판매할 종목을 선택해주세요.')
    for i in stock['holdings']:
        # 주가 최신화
        if i is None: break
        auction = dnfAPI.getItemAuctionPrice(i['name'])
        _, price = util.updateAuctionData(i['name'], auction)
        newPrice.append(price['평균가'])

        value = '매도 단가 : '  + format(price['평균가'], ',') + '\r\n'
        value += '매수 단가 : ' + format(i['bid'], ',') + '\r\n'
        value += '보유량 : '    + format(i['count'], ',')
        embed.add_field(name='> ' + i['name'], value=value)
    embed.set_footer(text='30초 안에 결정해야합니다.')
    await waiting.delete()
    msg = await ctx.channel.send(embed=embed)

    if len(stock['holdings']) >= 1: await msg.add_reaction('1️⃣')
    if len(stock['holdings']) >= 2: await msg.add_reaction('2️⃣')
    if len(stock['holdings']) >= 3: await msg.add_reaction('3️⃣')

    try:
        def check(reaction, user):
            return str(reaction) in ['1️⃣', '2️⃣', '3️⃣'] and user == ctx.author and reaction.message.id == msg.id
        reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)

        if str(reaction) == '1️⃣' and len(stock['holdings']) >= 1:
            await msg.delete()
            await sellStock(bot, ctx, stock, 0, newPrice[0])
        elif str(reaction) == '2️⃣' and len(stock['holdings']) >= 2:
            await msg.delete()
            await sellStock(bot, ctx, stock, 1, newPrice[1])
        elif str(reaction) == '3️⃣' and len(stock['holdings']) >= 3:
            await msg.delete()
            await sellStock(bot, ctx, stock, 2, newPrice[2])
    except asyncio.TimeoutError:
        await msg.delete()
        await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
    except Exception as e:
        await ctx.channel.send('> 오류가 발생했어요.\r\n> ' + str(e))

async def 주식랭킹(bot, ctx):
    await ctx.message.delete()
    waiting = await ctx.channel.send('> 주식 랭킹을 불러오는 중이예요...')

    try:
        conn, cur = connection.getConnection()
        sql = 'SELECT * FROM stock'
        cur.execute(sql)
        stocks = cur.fetchall()

        sql = 'SELECT * FROM auction'
        cur.execute(sql)
        auction = cur.fetchall()
    except Exception as e: return
    rank = getSortedStockRank(stocks, auction)

    if not rank:
        embed = discord.Embed(title='주식 랭킹을 알려드릴게요!',
                              description='> 랭킹 데이터가 없어요.\r\n'
                                          '> 여러분만의 주식을 보여주세요!')
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
            def check(reaction, user):
                return (str(reaction) == '◀️' or str(reaction) == '▶️') \
                       and user == ctx.author and reaction.message.id == msg.id
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

def isValid(did):
    try:
        conn, cur = connection.getConnection()
        sql = f'SELECT * FROM stock WHERE did={did}'
        cur.execute(sql)
        stock = cur.fetchone()
    except: return False
    if stock is not None:
        return True
    else:
        return False

def getHoldings(stock):
    holdings = []
    for i in [stock['holding1'], stock['holding2'], stock['holding3']]:
        if i is None: continue
        holding = json.loads(i)
        if holding is not None:
            holdings.append(holding)
    return holdings

async def buyStock(bot, ctx, name, price):
    stock = tool.getStock(ctx.message.author.id)
    if stock is None:
        embed = discord.Embed(title=ctx.message.author.display_name + '님의 매수 주문',
                              description='주식 정보를 찾을 수 없어요. `!주식` 명령어를 사용한 후에 다시 시도해주세요.')
        await ctx.channel.send(embed=embed)
        return

    stock['holdings'] = getHoldings(stock)

    # 추가 매수하는 경우
    isOverride = False
    for i in stock['holdings']:
        if i['name'] == name:
            isOverride = True
            break

    if len(stock['holdings']) >= 3 and not isOverride:
        embed = discord.Embed(title=ctx.message.author.display_name + '님의 매수 주문',
                              description='최대 3가지 종목만 보유할 수 있어요. `!주식매도` 명령어를 사용해서 보유한 주식을 매도할 수 있어요.')
        await ctx.channel.send(embed=embed)
        return

    embed = discord.Embed(title=ctx.message.author.display_name + '님의 매수 주문',
                          description=name + '을(를) 매수하실 양을 입력해주세요.')
    embed.add_field(name='> 보유 금액', value=format(stock['gold'], ',') + '골드')
    embed.add_field(name='> 매수 단가', value=format(price['평균가'], ',') + '골드')
    embed.add_field(name='> 매수 가능 갯수', value=format(stock['gold'] // price['평균가'], ',') + '개')
    embed.set_footer(text='30초 안에 결정해야합니다.')
    msg = await ctx.channel.send(embed=embed)

    try:
        def check(m):
            return ctx.channel.id == m.channel.id and ctx.message.author == m.author
        result = await bot.wait_for('message', check=check, timeout=30)
        bid, count = price['평균가'], int(result.content)

        # 0 이하
        if count <= 0:
            embed2 = discord.Embed(title=ctx.message.author.display_name + '님의 매수 주문',
                                   description='매수 갯수는 0 이하가 될 수 없어요. 다시 시도해주세요.')
            await result.delete()
            await msg.edit(embed=embed2)
            return

        # 초과 구매
        if count >= stock['gold'] // price['평균가']:
            embed2 = discord.Embed(title=ctx.message.author.display_name + '님의 매수 주문',
                                   description='매수 가능한 최대 갯수를 초과했어요. 다시 시도해주세요.')
            await result.delete()
            await msg.edit(embed=embed2)
            return

        # 추가 매수
        if isOverride:
            for i in stock['holdings']:
                if i['name'] == name:
                    newCount = count + i['count']
                    newBid   = ((bid * count) + (i['bid'] * i['count'])) // newCount
                    i['count'], i['bid'] = newCount, newBid
                    break

        # 첫 매수
        else:
            stock['holdings'].append({
                'name'  : name,
                'bid'   : bid,
                'count': count
            })

        stock['gold'] -= count * price['평균가']

        # 저장
        for i in range(3):
            try:    stock[f'holding{i + 1}'] = stock['holdings'][i]
            except: stock[f'holding{i + 1}'] = None

        try:
            conn, cur = connection.getConnection()
            sql = 'UPDATE stock SET gold=%s, holding1=%s, holding2=%s, holding3=%s WHERE did=%s'
            cur.execute(sql, (stock['gold'],
                              json.dumps(stock['holding1'], ensure_ascii=False),
                              json.dumps(stock['holding2'], ensure_ascii=False),
                              json.dumps(stock['holding3'], ensure_ascii=False),
                              ctx.message.author.id))
            conn.commit()
        except Exception as e:
            await ctx.channel.send(f'> 매수에 실패했어요.\r\n> {e}')
            return

        await msg.delete()
        await result.delete()
        embed2 = discord.Embed(title=ctx.message.author.display_name + '님의 매수 주문',
                               description=name + '을(를) 성공적으로 매수했습니다.')
        embed2.add_field(name='> 매수 단가', value=format(bid, ',') + '골드')
        embed2.add_field(name='> 매수량',    value=format(count, ',') + '개')
        embed2.add_field(name='> 매수금',    value=format(count * bid, ',') + '골드')
        await ctx.channel.send(embed=embed2)
    except asyncio.TimeoutError:
        await msg.delete()
        await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
    except Exception as e:
        await msg.delete()
        await result.delete()
        await ctx.channel.send('> 입력이 잘못되었어요. 다시 시도해주세요.')

async def sellStock(bot, ctx, stock, index, offer):
    did = ctx.message.author.id
    embed = discord.Embed(title=ctx.message.author.display_name + '님의 매도 주문',
                          description='매도할 양을 입력해주세요.\r\n매도 채결 시 1%의 수수료가 발생해요.')
    embed.add_field(name='> 종목', value=stock['holdings'][index]['name'])
    embed.add_field(name='> 매도 단가', value=format(offer, ',') + '골드')
    embed.add_field(name='> 매도 가능 갯수', value=format(stock['holdings'][index]['count'], ',') + '개')
    embed.set_footer(text='30초 안에 결정해야합니다.')
    msg = await ctx.channel.send(embed=embed)

    try:
        def check(m):
            return ctx.channel.id == m.channel.id and ctx.message.author == m.author
        result = await bot.wait_for('message', check=check, timeout=30)
        count = int(result.content)
        if count <= 0:
            await result.delete()
            embed2 = discord.Embed(title=ctx.message.author.display_name + '님의 매도 주문',
                                   description='매도 갯수는 0 이하가 될 수 없어요. 다시 시도해주세요.')
            await msg.edit(embed=embed2)
            return

        if count > stock['holdings'][index]['count']:
            await result.delete()
            embed2 = discord.Embed(title=ctx.message.author.display_name + '님의 매도 주문',
                                   description='매도 가능한 최대 갯수를 초과했습니다. 다시 시도해주세요.')
            await msg.edit(embed=embed2)
            return

        # 처리
        name = stock['holdings'][index]['name']
        stock['holdings'][index]['count'] -= count
        stock['gold'] += int(offer * count * 0.99)
        if stock['holdings'][index]['count'] <= 0:
            del stock['holdings'][index]

        # 저장
        for i in range(3):
            try:
                stock[f'holding{i + 1}'] = stock['holdings'][i]
            except:
                stock[f'holding{i + 1}'] = None

        try:
            conn, cur = connection.getConnection()
            sql = 'UPDATE stock SET gold=%s, holding1=%s, holding2=%s, holding3=%s WHERE did=%s'
            cur.execute(sql, (stock['gold'],
                              json.dumps(stock['holding1'], ensure_ascii=False),
                              json.dumps(stock['holding2'], ensure_ascii=False),
                              json.dumps(stock['holding3'], ensure_ascii=False), did))
            conn.commit()
        except Exception as e:
            await ctx.channel.send(f'> 매도에 실패했어요.\r\n> {e}')
            return

        await msg.delete()
        await result.delete()
        embed2 = discord.Embed(title=ctx.message.author.display_name + '님의 매도 주문',
                               description=name + '을(를) 성공적으로 매도했습니다.')
        embed2.add_field(name='> 매도 단가', value=format(offer, ',') + '골드')
        embed2.add_field(name='> 매도량', value=format(count, ',') + '개')
        embed2.add_field(name='> 매도금', value=format(int(count * offer * 0.99), ',') + '골드')
        await ctx.channel.send(embed=embed2)
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
        value = x['gold']
        for index in range(3):
            try:
                temp = json.loads(x[f'holding{index + 1}'])
                value += getRecentPrice(auction, temp['name']) * temp['count']
            except: pass
        return value
    return list(sorted(stocks, key=lambda x: key(x), reverse=True))

def getStockRankEmbed(ctx, rank, auction, page):
    rank = rank[page * 15:page * 15 + 15]

    embed = discord.Embed(title='주식 랭킹을 알려드릴게요!',
                          description='현재 어떤 주식을 보유중인지도 알려드려요.')
    for index, i in enumerate(rank):
        # name 계산
        name = f'> {page * 15 + index + 1}등'
        if i['did'] == str(ctx.message.author.id):
            name += f'({ctx.message.author.display_name}님)'

        # value 계산
        holdings = ''
        gold = i['gold']
        for j in range(3):
            try:
                temp = json.loads(i[f'holding{j + 1}'])
                holdings += f'종목{j + 1} : {temp["name"]}\r\n'
                gold += getRecentPrice(auction, temp['name']) * temp['count']
            except: pass
        value = f'{format(gold, ",")}골드\r\n{holdings}'
        embed.add_field(name=name, value=value)
    return embed

def getRecentPrice(auction, name):
    price = 0
    for i in auction:
        if i['name'] == name:
            price = i['price']
    return price

def getTotProfit(totBid, totGain):
    try:
        totProfit = (totGain / totBid - 1) * 100
        totProfit = float(format(totProfit, '.2f'))
        return makePlusMinus(totProfit)
    except:
        return '- 0.00%'

def getTotBit(stock):
    totBit = 0
    for i in stock['holdings']:
        try:
            totBit += i['bid'] * i['count']
        except: pass
    return totBit

def getTotGain(stock, newPrice):
    totGain = 0
    for i in range(len(stock['holdings'])):
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