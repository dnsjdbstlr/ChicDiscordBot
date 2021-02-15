import json
import discord
import asyncio
from src import dnfAPI, util
from datetime import datetime
from database import connection

def iniStock(conn, cur, did):
    sql = f'INSERT INTO stock (did, gold) values ({did}, {10000000})'
    cur.execute(sql)
    conn.commit()

def getHoldings(stock):
    holdings = []
    for i in [stock['holding1'], stock['holding2'], stock['holding3']]:
        if i is not None and i != 'null':
            holdings.append(json.loads(i))
    return holdings

async def 출석(bot, ctx):
    await ctx.message.delete()
    waiting = await ctx.channel.send(f'> {ctx.message.author.display_name}님의 출석을 확인하고있어요...')
    did = str(ctx.message.author.id)
    today = datetime.now().strftime('%Y-%m-%d')

    # 커넥션
    conn, cur = connection.db.getConnection()

    # 주식 정보 확인
    try:
        sql = f'SELECT * FROM stock WHERE did={did}'
        cur.execute(sql)
        stock = cur.fetchone()
    except Exception as e:
        await ctx.channel.send(f'> 주식 정보를 불러오지 못했어요.\r\n> {e}')
        return

    if stock is None:
        text = f'> {ctx.message.author.display_name}님의 주식 정보를 찾을 수 없어요.\r\n'
        text += '> !주식 명령어를 사용한 후 다시 입력해주세요.'
        await waiting.delete()
        await ctx.channel.send(text)
        return

    # 출석 체크 확인
    try:
        sql = f'SELECT * FROM dailyCheck WHERE did={did}'
        cur.execute(sql)
        daily = cur.fetchone()
    except Exception as e:
        await ctx.channel.send(f'> 출석 정보를 불러오지 못했어요.\r\n> {e}')
        return

    if daily is not None and str(daily.get('date')) == today:
        text = f'> {ctx.message.author.display_name}님은 이미 출석체크 하셨어요.\r\n'
        text += '> 출석체크는 매일 00시에 초기화되요!'
        await waiting.delete()
        await ctx.channel.send(text)
        return

    # 출석 처리
    try:
        # 보상 지급
        sql = f'SELECT gold FROM stock WHERE did={did}'
        cur.execute(sql)
        rs = cur.fetchone()

        reward = util.getDailyReward()
        gold = rs['gold'] + reward

        sql = f'UPDATE stock SET gold={gold} WHERE did={did}'
        cur.execute(sql)
        conn.commit()

        # 처음 출석
        sql = 'INSERT INTO dailyCheck (did, count, date) values (%s, %s, %s)'
        cur.execute(sql, (did, 1, today))
        conn.commit()
    except:
        # 출석 최신화
        sql = 'UPDATE dailyCheck SET count=%s, date=%s WHERE did=%s'
        cur.execute(sql, (daily['count'] + 1, today, did))
        conn.commit()

    infoSwitch = True
    embed = getDailyCheckInfoEmbed(ctx.message.author.display_name, today, daily, reward)
    await waiting.delete()
    msg = await ctx.channel.send(embed=embed)
    await msg.add_reaction('▶️')

    while True:
        try:
            def check(reaction, user):
                return (str(reaction) == '◀️' or str(reaction) == '▶️') \
                       and user == ctx.author and reaction.message.id == msg.id
            reaction, user = await bot.wait_for('reaction_add', check=check)

            if infoSwitch and str(reaction) == '▶️':
                embed = getRewardInfoEmbed()
                await msg.edit(embed=embed)
                await msg.clear_reactions()
                await msg.add_reaction('◀️')
                infoSwitch = not infoSwitch
            if not infoSwitch and str(reaction) == '◀️':
                embed = getDailyCheckInfoEmbed(ctx.message.author.display_name, today, daily, reward)
                await msg.edit(embed=embed)
                await msg.clear_reactions()
                await msg.add_reaction('▶️')
                infoSwitch = not infoSwitch
        except:
            await msg.delete()
            await ctx.channel.send('> 오류가 발생했어요.')

def getDailyCheckInfoEmbed(name, today, daily, reward):
    embed = discord.Embed(title=f'{name}님 출석체크 완료!')
    embed.add_field(name='> 출석 날짜', value=today)
    embed.add_field(name='> 출석 일수', value=str(daily['count'] + 1) + '일')
    embed.add_field(name='> 출석 보상', value=format(reward, ',') + '골드')
    embed.set_footer(text='매일 00시마다 초기화되요.')
    return embed

def getRewardInfoEmbed():
    embed = discord.Embed(title='출석 보상 확률을 알려드릴게요.')
    embed.add_field(name='> 0골드', value='1%')
    embed.add_field(name='> 100,000골드', value='1%')
    embed.add_field(name='> 200,000골드', value='4%')
    embed.add_field(name='> 300,000골드', value='8%')
    embed.add_field(name='> 400,000골드', value='16%')
    embed.add_field(name='> 500,000골드', value='20%')
    embed.add_field(name='> 600,000골드', value='20%')
    embed.add_field(name='> 700,000골드', value='16%')
    embed.add_field(name='> 800,000골드', value='8%')
    embed.add_field(name='> 900,000골드', value='4%')
    embed.add_field(name='> 1,000,000골드', value='1%')
    embed.add_field(name='> 2,000,000골드', value='1%')
    embed.set_footer(text='평균 기대값은 559,000골드예요.')
    return embed

async def 주식(ctx):
    await ctx.message.delete()
    waiting = await ctx.channel.send('> ' + ctx.message.author.display_name + '님의 주식 정보를 불러오고 있어요...')
    did = str(ctx.message.author.id)

    # 커넥션
    conn, cur = connection.db.getConnection()

    try:
        sql = f'SELECT * FROM stock WHERE did={did}'
        cur.execute(sql)
        stock = cur.fetchone()
    except Exception as e:
        await ctx.channel.send(f'> 주식 정보를 불러오지 못했어요.\r\n> {e}')
        return

    # 초기세팅
    if stock is None:
        iniStock(conn, cur, did)
        sql = f'SELECT * FROM stock WHERE did={did}'
        cur.execute(sql)
        stock = cur.fetchone()

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
            volatility = util.getVolatility2(holdings['bid'], newPrice[i])

            name = '> ' + holdings['name']
            value = '현재 단가 : ' + format(newPrice[i], ',') + '골드\r\n'
            value += '매수 단가 : ' + format(holdings['bid'], ',') + '골드\r\n'
            value += '매수량 : ' + format(holdings['count'], ',') + '개\r\n'
            #value += '매수금 : ' + format(holdings['bid'] * holdings['count'], ',') + '골드\r\n'
            value += '수익률 : ' + volatility
        except Exception as e:
            name = '> 종목' + str(i + 1)
            value = '보유 중인 주식이 없습니다.'
            #print(e)
        embed.add_field(name=name, value=value)
    await waiting.delete()
    await ctx.channel.send(embed=embed)

async def 주식매수(bot, ctx, *input):
    await ctx.message.delete()

    if not input:
        await ctx.channel.send("> !주식매수 '아이템이름' 의 형태로 적어야해요!")
        return

    waiting = await ctx.channel.send('> 해당 주식의 정보를 불러오는 중입니다...')

    name = util.mergeString(*input)
    name = dnfAPI.getMostSimilarItemName(name)

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
                          description=name + ' 시세 정보입니다.\r\n매수하려면 O, 취소하려면 X 이모지를 눌러주세요.')
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
            did = str(ctx.message.author.id)
            await buyStock(bot, ctx, did, name, price)
        elif str(reaction) == '❌':
            await msg.delete()
            await ctx.channel.send('> 매수가 취소되었습니다.')
    except asyncio.TimeoutError:
        await msg.delete()
        await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
    except Exception as e:
        await ctx.channel.send('> 오류가 발생했어요.\r\n> ' + str(e))

async def buyStock(bot, ctx, did, name, price):
    conn, cur = connection.db.getConnection()
    try:
        sql = f'SELECT * FROM stock WHERE did={did}'
        cur.execute(sql)
        stock = cur.fetchone()
    except Exception as e:
        await ctx.channel.send(f'> 주식 정보를 불러오지 못했어요.\r\n> {e}')
        return

    if stock is None:
        text = f'> {ctx.message.author.display_name}님의 주식 정보를 찾을 수 없어요.\r\n'
        text += '> !주식 명령어를 사용한 후 다시 입력해주세요.'
        await ctx.channel.send(text)
        return

    stock['holdings'] = getHoldings(stock)

    # 추가 매수하는 경우
    isOverride = False
    for i in stock['holdings']:
        if i['name'] == name:
            isOverride = True

    if len(stock['holdings']) >= 3 and not isOverride:
        text = '> 최대 3가지 종목만 보유할 수 있어요.\r\n'
        text += '> 보유 중인 주식을 매도하고 다시 시도해주세요.'
        await ctx.channel.send(text)
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
            try:
                stock[f'holding{i + 1}'] = stock['holdings'][i]
            except:
                stock[f'holding{i + 1}'] = None

        try:
            sql = 'UPDATE stock SET gold=%s, holding1=%s, holding2=%s, holding3=%s WHERE did=%s'
            cur.execute(sql, (stock['gold'],
                              json.dumps(stock['holding1'], ensure_ascii=False),
                              json.dumps(stock['holding2'], ensure_ascii=False),
                              json.dumps(stock['holding3'], ensure_ascii=False), did))
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

async def 주식매도(bot, ctx):
    await ctx.message.delete()
    waiting = await ctx.channel.send(f'> {ctx.message.author.display_name}님의 보유 주식을 불러오는 중입니다...')
    did = str(ctx.message.author.id)

    # 커넥션
    conn, cur = connection.db.getConnection()

    try:
        sql = f'SELECT * FROM stock WHERE did={did}'
        cur.execute(sql)
        stock = cur.fetchone()
    except Exception as e:
        await ctx.channel.send(f'> 주식 정보를 불러오지 못했어요.\r\n> {e}')
        return

    if stock is None:
        text = f'> {ctx.message.author.display_name}님의 주식 정보를 찾을 수 없어요.\r\n'
        text += '> !주식 명령어를 사용한 후 다시 입력해주세요.'
        await ctx.channel.send(text)
        return

    stock['holdings'] = getHoldings(stock)
    if len(stock['holdings']) == 0:
        await waiting.delete()
        await ctx.channel.send(f'> {ctx.message.author.display_name}님은 매도할 주식이 없어요.')
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

    if len(stock['holdings']) >= 1:
        await msg.add_reaction('1️⃣')
    if len(stock['holdings']) >= 2:
        await msg.add_reaction('2️⃣')
    if len(stock['holdings']) >= 3:
        await msg.add_reaction('3️⃣')

    try:
        def check(reaction, user):
            return str(reaction) in ['1️⃣', '2️⃣', '3️⃣'] and user == ctx.author and reaction.message.id == msg.id
        reaction, user = await bot.wait_for('reaction_add', check=check, timeout=30)

        if str(reaction) == '1️⃣' and len(stock['holdings']) >= 1:
            await msg.delete()
            await sellStock(bot, ctx, did, stock, 0, newPrice[0])
        elif str(reaction) == '2️⃣' and len(stock['holdings']) >= 2:
            await msg.delete()
            await sellStock(bot, ctx, did, stock, 1, newPrice[1])
        elif str(reaction) == '3️⃣' and len(stock['holdings']) >= 3:
            await msg.delete()
            await sellStock(bot, ctx, did, stock, 2, newPrice[2])
    except asyncio.TimeoutError:
        await msg.delete()
        await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
    except Exception as e:
        await ctx.channel.send('> 오류가 발생했어요.\r\n> ' + str(e))

async def sellStock(bot, ctx, did, stock, index, offer):
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
            conn, cur = connection.db.getConnection()
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

async def 주식랭킹(bot, ctx):
    await ctx.message.delete()
    waiting = await ctx.channel.send('> 주식 랭킹을 불러오는 중이예요...')

    try:
        conn, cur = connection.db.getConnection()
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

    embed = discord.Embed(title='타이틀', description='설명')
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
