import discord
import asyncio
import json
from SRC import DNFAPI, Util

class playerStockData:
    def __init__(self):
        self.data = {}

        try:
            with open('Data/playerStockData.json', 'r') as f:
                print('[알림][주식 데이터를 불러왔습니다.]')
                self.data = json.load(f)
        except:
            print('[알림][주식 데이터가 없습니다.]')

    def update(self):
        with open('Data/playerStockData.json', 'w') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
STOCK_DATA = playerStockData()

async def 출석(ctx):
    await ctx.message.delete()
    pid = str(ctx.message.author.id)
    stock = STOCK_DATA.data.get(pid)

    if stock is None:
        text = '> ' + ctx.message.author.display_name + '님의 주식 정보를 찾을 수 없어요.\r\n'
        text += '> !주식 명령어를 사용한 후 다시 입력해주세요.'
        await ctx.channel.send(text)
        return

    if stock['daily'] == Util.getToday2():
        text = '> ' + ctx.message.author.display_name + '님은 오늘 이미 출석체크 하셨어요.\r\n'
        text += '> 내일(09시) 다시 찾아와서 해주세요!'
        await ctx.channel.send(text)
        return

    ### 보상 지급 ###
    stock['daily'] = Util.getToday2()
    stock['money'] += 1000000
    STOCK_DATA.update()

    text = '> ' + ctx.message.author.display_name + '님 출석체크 완료!\r\n'
    text += '> 주식 계좌에 1,000,000골드를 지급해드렸어요!'
    await ctx.channel.send(text)

async def 주식(ctx):
    await ctx.message.delete()
    waiting = await ctx.channel.send('> ' + ctx.message.author.display_name + '님의 주식 정보를 불러오고 있어요...')

    pid = str(ctx.message.author.id)
    stock = STOCK_DATA.data.get(pid)

    ### 초기세팅 ###
    if stock is None:
        ini = {
            'daily': 'NULL',
            'money': 10000000,
            'buy'  : 0,
            'sell' : 0,
            'holdings': []
        }
        STOCK_DATA.data.update({pid: ini})
        STOCK_DATA.update()
        stock = STOCK_DATA.data.get(pid)

    ### 주가 최신화 ###
    newPrice = []
    for i in stock['holdings']:
        name = Util.mergeString(i['name'])
        name = DNFAPI.getMostSimilarItemName(name)
        soldInfo = DNFAPI.getItemAuctionPrice(name)
        price, _ = Util.updateAuctionData(name, soldInfo)
        newPrice.append(price['평균가'])

    ### 계산 ###
    money = format(stock['money'], ',') + '골드'
    totBid = getTotBit(stock)
    totGain = getTotGain(stock, newPrice)
    totProfit = getTotProfit(totBid, totGain)

    ### 출력 ###
    embed = discord.Embed(title=ctx.message.author.display_name + '님의 주식 정보를 알려드릴게요.')
    embed.add_field(name='> 보유 금액', value=money, inline=False)
    embed.add_field(name='> 총 수익률', value=totProfit)
    embed.add_field(name='> 총 매수금', value=format(totBid, ',') + '골드')
    embed.add_field(name='> 총 평가금', value=format(totGain, ',') + '골드')

    for i in range(3):
        try:
            holdings = stock['holdings']
            volatility = (newPrice[i] / holdings[i]['bid'] - 1) * 100
            volatility = float(format(volatility, '.2f'))
            if volatility > 0:
                volatility = '▲ ' + str(volatility) + '%'
            elif volatility == 0:
                volatility = '- 0.00%'
            else:
                volatility = '▼ ' + str(volatility) + '%'
            name = '> ' + holdings[i]['name']
            value = '현재 단가 : ' + format(newPrice[i], ',') + '골드\r\n'
            value += '매수 단가 : ' + format(holdings[i]['bid'], ',') + '골드\r\n'
            value += '매수량 : ' + format(holdings[i]['count'], ',') + '개\r\n'
            value += '매수금 : ' + format(holdings[i]['bid'] * holdings[i]['count'], ',') + '골드\r\n'
            value += '수익률 : ' + volatility
        except:
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

    name = Util.mergeString(*input)
    name = DNFAPI.getMostSimilarItemName(name)
    soldInfo = DNFAPI.getItemAuctionPrice(name)
    await waiting.delete()

    if not soldInfo:
        await ctx.channel.send('> 해당 아이템의 판매 정보를 얻어오지 못했어요.')
        return

    data, volatility = Util.updateAuctionData(name, soldInfo)
    embed = discord.Embed(title=name + '의 실시간 정보입니다.',
                          description='매수하려면 O, 취소하려면 X 이모지를 눌러주세요.')
    embed.add_field(name='> 단가', value=format(data['평균가'], ',') + '골드')
    embed.add_field(name='> 최근 판매량', value=format(data['판매량'], ',') + '개')
    embed.add_field(name='> 가격 변동률', value=volatility)
    embed.set_footer(text='10초 안에 결정해야합니다.')
    embed.set_thumbnail(url=DNFAPI.getItemImageUrl(soldInfo[0]['itemId']))
    msg = await ctx.channel.send(embed=embed)

    await msg.add_reaction('⭕')
    await msg.add_reaction('❌')

    try:
        def check(reaction, user):
            return (str(reaction) == '⭕' or str(reaction) == '❌') \
                   and user == ctx.author and reaction.message.id == msg.id
        reaction, user = await bot.wait_for('reaction_add', check=check, timeout=10)

        if str(reaction) == '⭕':
            await msg.delete()
            pid = str(ctx.message.author.id)
            await buyStock(bot, ctx, pid, name, data)
        elif str(reaction) == '❌':
            await msg.delete()
            await ctx.channel.send('> 매수가 취소되었습니다.')
    except asyncio.TimeoutError:
        await msg.delete()
        await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
    except:
        await msg.delete()
        await ctx.channel.send('> 오류가 발생했어요.')

async def buyStock(bot, ctx, pid, name, data):
    stock = STOCK_DATA.data.get(pid)
    if stock is None:
        text = '> ' + ctx.message.author.display_name + '님의 주식 정보를 찾을 수 없어요.\r\n'
        text += '> !주식 명령어를 사용한 후 다시 입력해주세요.'
        await ctx.channel.send(text)
        return

    ### 이미 갖고있는 종목 구매 ###
    isOverride = False
    for i in stock['holdings']:
        if i['name'] == name:
            isOverride = True

    if len(stock['holdings']) >= 3 and not isOverride:
        text = '> 최대 3가지 종목만 보유할 수 있어요.\r\n'
        text += '> 보유 중인 주식을 매도하고 다시 시도해주세요.'
        await ctx.channel.send(text)
        return

    embed = discord.Embed(title=name + ' 매수',
                          description='매수하실 양을 입력해주세요.')
    embed.add_field(name='> 보유 금액', value=format(stock['money'], ',') + '골드')
    embed.add_field(name='> 매수 가능 갯수', value=format(stock['money'] // data['평균가'], ',') + '개')
    embed.add_field(name='> 단가', value=format(data['평균가'], ',') + '골드')
    embed.set_footer(text='30초 안에 결정해야합니다.')
    msg = await ctx.channel.send(embed=embed)

    try:
        def check(m):
            return ctx.channel.id == m.channel.id and ctx.message.author == m.author
        result = await bot.wait_for('message', check=check, timeout=30)
        bid, count = data['평균가'], int(result.content)

        ### 매수 처리 ###
        stock['money'] -= count * data['평균가']

        ### 추가 매수 ###
        if isOverride:
            for i in stock['holdings']:
                if i['name'] == name:
                    newCount = count + i['count']
                    newBid = ((bid * count) + (i['bid'] * i['count'])) // newCount
                    i['bid'], i['count'] = newBid, newCount
                    break

        ### 처음 매수 ###
        else:
            stock['holdings'].append({
                'name'  : name,
                'bid'   : bid,
                'count': count
            })

        try:
            stock['buy'] += 1
        except:
            stock['buy'] = 1
        STOCK_DATA.update()

        await msg.delete()
        await result.delete()
        embed2 = discord.Embed(title=ctx.message.author.display_name + '님의 매수 주문', description=name + '을(를) 성공적으로 매수했습니다.')
        embed2.add_field(name='> 매수 가격', value=format(bid, ',') + '골드')
        embed2.add_field(name='> 매수량', value=format(count, ',') + '개')
        embed2.add_field(name='> 매수금', value=format(count * bid, ',') + '골드')
        await ctx.channel.send(embed=embed2)

    except asyncio.TimeoutError:
        await msg.delete()
        await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
    except:
        await msg.delete()
        await ctx.channel.send('> 입력이 잘못되었어요. 다시 시도해주세요.')

async def 주식매도(bot, ctx):    
    await ctx.message.delete()
    waiting = await ctx.channel.send('> 보유 주식의 정보를 불러오는 중입니다...')

    pid = str(ctx.message.author.id)
    stock = STOCK_DATA.data.get(pid)

    if stock is None:
        await waiting.delete()
        text = '> ' + ctx.message.author.display_name + '님의 주식 정보를 찾을 수 없어요.\r\n'
        text += '> !주식 명령어를 사용한 후 다시 입력해주세요.'
        await ctx.channel.send(text)
        return

    if len(stock['holdings']) == 0:
        await waiting.delete()
        await ctx.channel.send('> ' + ctx.message.author.display_name + '님은 매도할 주식이 없어요.')
        return

    newPrice = []
    embed = discord.Embed(title='판매할 종목을 선택해주세요.')
    for i in stock['holdings']:
        ### 주가 최신화 ###
        name = Util.mergeString(i['name'])
        name = DNFAPI.getMostSimilarItemName(name)
        soldInfo = DNFAPI.getItemAuctionPrice(name)
        price, _ = Util.updateAuctionData(name, soldInfo)
        newPrice.append(price['평균가'])

        value = '매도 단가 : ' + format(price['평균가'], ',') + '\r\n'
        value += '매수 단가 : ' + format(i['bid'], ',') + '\r\n'
        value += '보유량 : ' + format(i['count'], ',')
        embed.add_field(name='> ' + i['name'], value=value)
    embed.set_footer(text='10초 안에 결정해야합니다.')
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
        reaction, user = await bot.wait_for('reaction_add', check=check, timeout=10)

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
    except:
        await ctx.channel.send('> 오류가 발생했어요.')

async def sellStock(bot, ctx, stock, index, offer):
    embed = discord.Embed(title='매도할 양을 입력해주세요.', description='매도 채결 시 1%의 수수료가 발생해요.')
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
        if count > stock['holdings'][index]['count']:
            await msg.delete()
            await ctx.channel.send('> 매도 가능한 갯수를 초과했습니다.')
            return

        ### 매도 처리 ###
        name = stock['holdings'][index]['name']
        stock['holdings'][index]['count'] -= count
        stock['money'] += int(offer * count * 0.99)
        if stock['holdings'][index]['count'] == 0:
            del stock['holdings'][index]

        try:
            stock['sell'] += 1
        except:
            stock['sell'] = 1
        STOCK_DATA.update()

        await msg.delete()
        await result.delete()
        embed2 = discord.Embed(title=ctx.message.author.display_name + '님의 매도 주문',
                               description=name + '을(를) 성공적으로 매도했습니다.')
        embed2.add_field(name='> 매도 단가', value=format(offer, ',') + '골드')
        embed2.add_field(name='> 매도량', value=format(count, ',') + '개')
        embed2.add_field(name='> 수익금', value=format(int(count * offer * 0.99), ',') + '골드')
        await ctx.channel.send(embed=embed2)
    except asyncio.TimeoutError:
        await msg.delete()
        await ctx.channel.send('> 시간 끝! 더 고민해보고 다시 불러주세요.')
    except:
        await msg.delete()
        await ctx.channel.send('> 오류가 발생했어요.')

async def 주식랭킹(ctx):
    await ctx.message.delete()
    rank = getStockRank()
    embed = discord.Embed(title='주식 랭킹을 알려드릴게요!',
                          description='보유금액 + 평가금액으로 순위를 매기며 15등까지만 보여드려요.')

    for index, key in enumerate(rank.keys()):
        stocks = ''                 # 종목
        #buy    = rank[key]['buy']   # 매수 횟수
        #sell   = rank[key]['sell']  # 매도 횟수
        money  = rank[key]['money'] # 보유금
        price  = 0                  # 평가금

        ### 종목, 평가금 계산 ###
        for _index, i in enumerate(rank[key]['holdings']):
            stocks += '종목' + str(_index + 1) + ' : ' + i['name'] + '\r\n'
            price += Util.getRecentAuctionPrice(i['name']) * i['count']

        ### 결과 세팅 ###
        value = format(money + price, ',') + '골드\r\n'
        #value += '보유금 : ' + format(money, ',') + '골드\r\n'
        #value += '평가금 : ' + format(price, ',') + '골드\r\n'
        #value += '매수/매도 : ' + format(buy, ',') + '회/' + format(sell, ',') + '회\r\n'
        value += stocks
        name = '> ' + str(index + 1) + '등'

        ### 본인 표시 ###
        if key == str(ctx.message.author.id):
            name += '(' + ctx.message.author.display_name + '님)'

        embed.add_field(name=name, value=value)

    await ctx.channel.send(embed=embed)

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
        totBit += i['bid'] * i['count']
    return totBit

def getTotGain(stock, newPrice):
    totGain = 0
    for i in range(len(stock['holdings'])):
        totGain += newPrice[i] * stock['holdings'][i]['count']
    return totGain

def makePlusMinus(num):
    if num >= 0:
        num = '▲ ' + format(num, ',') + '%'
    elif num == 0:
        num = '- 0.00%'
    else:
        num = '▼ ' + format(num, ',') + '%'
    return num

def getStockRank():
    def key(x):
        criterion = x[1]['money']
        for i in x[1]['holdings']:
            price = Util.getRecentAuctionPrice(i['name'])
            criterion += price * i['count']
        return criterion
    return dict(sorted(STOCK_DATA.data.items(), key=key, reverse=True)[:15])
