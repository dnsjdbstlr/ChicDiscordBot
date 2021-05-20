import asyncio
import discord
import json
from datetime import datetime, date, timedelta
from Database import Tool
from Src import DNFAPI

async def 선물거래(ctx):
    await ctx.message.delete()
    did = ctx.author.id

    # account가 없을 경우
    if Tool.getAccount(did) is None:
        Tool.iniAccount(did)

    # stock이 없을 경우
    stock = Tool.getStock(did)
    if stock is None: Tool.iniStock(did)
    stock = Tool.getStock(did)

    embed = discord.Embed(title='던파 경매장 선물 거래에 대해 설명해드릴게요!')
    embed.add_field(name='> 선물 거래가 뭔가요?', inline=False,
                    value='''미래에 해당 종목의 가격이 어떻게 될지 맞추는 거래예요.
                          가격이 오를 것 같으면 `매수(롱)`, 떨어질 것 같으면 `매도(숏)` 포지션을 잡으면 되요.
                          포지션을 잡을 때는 레버리지를 설정해야해요. 레버리지는 배율이라고 생각할 수 있어요.
                          예를 들어 레버리지 5배 롱 포지션을 잡았을 때 종목의 가격이 `1% 오르면 5%의 수익`을 볼 수 있어요. 하지만 그 반대로 1% 떨어지면 -5%의 손해를 볼 수 있어요.''')

    embed.add_field(name='> 청산 가격은 뭔가요?', inline=False,
                    value='''해당 종목의 가격이 청산 가격에 도달하면 해당 포지션은 `자동으로 청산` 당하게 되요.
                          청산 당했다는 것은 손익률이 -100%가 되었다는 뜻이에요. 레버리지가 높으면 그만큼 변동성이 크니 쉽게 청산당할 수 있어요.''')

    embed.add_field(name='> 돈을 모두 잃었어요. 어떻게 해야되나요?', inline=False,
                    value='''`!파산` 명령어를 사용해 처음부터 다시 시작할 수 있어요.
                          하지만 `!파산` 명령어를 사용하고 3일이 지나야 선물 거래를 할 수 있어요.''')

    embed.add_field(name='> 어떤 종목들이 있나요?', inline=False,
                    value='''다음 6개의 종목들에 대해서만 매수/매도 할 수 있어요.
                          `아이올라이트`, `시간의 결정`, `고대 지혜의 잔해`,
                          `힘의 정수 1개 상자`, `무색큐브조각`, `모순의 결정체`''')

    embed.add_field(name='> 관련 다른 명령어는 어떤게 있나요?', inline=False,
                    value='''`!주문 <종목> <레버리지>` : 해당 포지션에 진입해요. 레버리지는 -50 ~ 50사이만 가능해요.
                          `!포지션` : 본인이 현재 보유 중인 포지션을 확인하고 종료할 수 있어요.
                          `!거래랭킹` : 보유금 + 평가금을 기준으로한 랭킹을 볼 수 있어요. 
                    ''')

    embed.add_field(name='> 주문 예시는 다음과 같아요', inline=False,
                    value='''`!주문 아이올라이트 10` : 아이올라이트 x10 매수(롱)
                          `!주문 시간의 결정 -20` : 시간의 결정 x20 매도(숏)
                          `!주문 무색 큐브 조각` : 무색 큐브 조각 x1 매수(롱)
                    ''')

    await ctx.channel.send(embed=embed)

async def 주문(bot, ctx, *inputs):
    await ctx.message.delete()
    did, name = ctx.message.author.id, ctx.message.author.display_name

    # account가 없을 경우
    if Tool.getAccount(did) is None:
        Tool.iniAccount(did)

    # stock이 없을 경우
    stock = Tool.getStock(did)
    if stock is None: Tool.iniStock(did)
    stock = Tool.getStock(did)

    # 거래 금지인 경우
    today = datetime.today()
    if date(today.year, today.month, today.day) < stock['allowDate']:
        await ctx.channel.send(f"> {name}님은 {stock['allowDate']}부터 선물거래가 가능해요.")
        return

    # 입력이 잘못됬을 경우
    if len(inputs) == 0:
        await ctx.channel.send('> `!주문 <레버리지> <선물거래>` 의 형태로 다시 시도해주세요.')
        return

    # 레버리지, 종목명
    try:
        leverage = int(inputs[-1])
        stockName = ' '.join(inputs[:-1])
    except ValueError:
        leverage = 1
        stockName = ' '.join(inputs)

    if leverage == 0 or abs(leverage) > 50:
        await ctx.channel.send('> 레버리지는 -50 ~ 50까지만 가능해요.\n> 레버리지를 다시 정해서 시도해주세요!')
        return

    orderType = '매수(롱)' if leverage > 0 else '매도(숏)'

    if stockName not in ['아이올라이트', '시간의 결정', '고대 지혜의 잔해',
                         '힘의 정수 1개 상자', '무색 큐브 조각', '모순의 결정체']:
        await ctx.channel.send('> 다음 종목들에 대해서만 주문을 넣을 수 있어요.\n'
                               '> `아이올라이트`, `시간의 결정`, `고대 지혜의 잔해`,\n'
                               '> `힘의 정수 1개 상자`, `무색큐브조각`, `모순의 결정체`')
        return

    item        = DNFAPI.getMostSimilarItem(stockName)
    latestBid   = Tool.getLatestPrice(stockName)
    prevBid     = Tool.getPrevPrice(stockName)
    gold        = Tool.getGold(did)
    margin  = int(latestBid['price'] * (1 - (1 / leverage) ))

    # 출력에 필요한 데이터 세팅
    val_bid = f"{format(latestBid['price'], ',')}골드"

    if prevBid is None:
        val_rate = '데이터 없음'
    else:
        rate = (latestBid['price'] / prevBid['price'] - 1) * 100
        val_rate = f"▼ {format(rate, '.2f')}%" if rate < 0 else f"▲ {format(rate, '.2f')}%"

    val_leverage = f"x{abs(leverage)}"
    val_margin = f"{format(margin, ',')}골드"
    val_max = f"{format(gold // latestBid['price'], ',')}개"
    val_wallet = f"{format(gold, ',')}골드"
    
    embed = discord.Embed(title=f"{name}님의 {orderType} 주문",
                          description=f"아래의 내용을 확인하고 {'매수량' if orderType else '매도량'}을 적어주세요.\n"
                                      '10초안에 입력하지 않으면 자동으로 주문이 취소되요.')
    embed.set_thumbnail(url=DNFAPI.getItemImageUrl(item['itemId']))
    embed.add_field(name='> 종목명', value=stockName)
    embed.add_field(name='> 현재가', value=val_bid)
    embed.add_field(name='> 등락률', value=val_rate)
    embed.add_field(name='> 레버리지', value=val_leverage)
    embed.add_field(name='> 청산가', value=val_margin)
    embed.add_field(name='> 최대 사이즈', value=val_max)
    embed.set_footer(text=f"지갑 잔고 : {val_wallet}")
    question = await ctx.channel.send(embed=embed)

    try:
        def check(_message):
            return ctx.channel.id == _message.channel.id and ctx.message.author == _message.author
        answer = await bot.wait_for('message', check=check, timeout=10)

        if not answer.content.isnumeric() or int(answer.content) <= 0 or int(answer.content) > gold // latestBid['price']:
            await answer.delete()
            await question.edit(content=f"> {name}님의 {orderType} 주문이 취소되었어요.\n"
                                        f"> 입력이 잘못되었어요. 1 ~ {gold // latestBid['price']}의 숫자만 입력해야해요.", embed=None)
            return

        # 보유 가능 갯수 초과
        stock = Tool.getStock(did)
        wallet = json.loads(stock['wallet'])
        if len(wallet['wallet']) >= 3:
            await answer.delete()
            await question.edit(content=f"> {name}님의 {orderType} 주문이 취소되었어요.\n"
                                        '> 최대 3가지 종목까지 보유할 수 있어요. 보유한 포지션을 종료한 후 다시 시도해주세요.', embed=None)
            return

        await answer.delete()
        embed = discord.Embed(title=f"{name}님의 {orderType} 주문",
                              description='주문이 성공적으로 채결됬습니다. 아래 내용을 확인해주세요.\n'
                                          '`!포지션` 명령어를 현재 자신의 포지션들을 확인할 수 있어요.')
        embed.set_thumbnail(url=DNFAPI.getItemImageUrl(item['itemId']))
        embed.add_field(name='> 종목명', value=stockName)
        embed.add_field(name='> 사이즈', value=f"{answer.content}개")
        embed.add_field(name='> 레버리지', value=val_leverage)
        await question.edit(embed=embed)

        data = {
            'stock'     : stockName,
            'leverage'  : leverage,
            'size'      : int(answer.content),
            'bid'       : latestBid['price'],
            'margin'    : margin
        }
        Tool.addStock(did, data)
        Tool.gainGold(did, -int(answer.content) * latestBid['price'])

    except asyncio.TimeoutError:
        await question.edit(content=f"> {name}님의 {orderType} 주문이 취소되었어요.\n"
                                    f"> 10초안에 {'매수량' if orderType else '매도량'}을 입력하지 않아서 자동으로 취소되었어요.", embed=None)
    except: return

async def 포지션(bot, ctx):
    def MAKE_EMBED(_wallet):
        _did, _name = ctx.message.author.id, ctx.message.author.display_name
        embed = discord.Embed(title=f"{_name}님의 포지션",
                              description='종료하고 싶은 포지션이 있다면 해당 번호의 이모지를 눌러주세요.\n'
                                          '이모지를 누르면 즉시 해당 포지션을 종료합니다.')
        for _w in _wallet['wallet']:
            _price = Tool.getLatestPrice(_w['stock'])['price']
            rate = (_price / _w['bid'] - 1) * 100 * _w['leverage']
            rate = format(rate, '.2f')
            temp = format(float(rate), ',')
            val_rate = f"▲ {temp}%" if float(rate) >= 0 else f"▼ {temp}%"

            _name = f"> {_w['stock']} x{abs(_w['leverage'])}{'롱' if _w['leverage'] > 0 else '숏'}"
            value = f"사이즈       : {format(_w['size'], ',')}개\n"
            value += f"진입 가격    : {format(_w['bid'], ',')}골드\n"
            value += f"현재 가격    : {format(_price, ',')}골드\n"
            value += f"청산 가격    : {format(_w['margin'], ',')}골드\n"
            value += f"손익률       : {val_rate}"
            embed.add_field(name=_name, value=value)

        for i in range( len(_wallet['wallet']), 3 ):
            embed.add_field(name=f"> 포지션{i + 1}", value='없음')

        embed.set_footer(text=f"지갑 잔고 : {format(Tool.getGold(_did), ',')}골드")
        return embed

    await ctx.message.delete()
    did = ctx.message.author.id

    # account가 없을 경우
    if Tool.getAccount(did) is None:
        Tool.iniAccount(did)

    # stock이 없을 경우
    stock = Tool.getStock(did)
    if stock is None: Tool.iniStock(did)
    stock = Tool.getStock(did)

    wallet = json.loads(stock['wallet'])
    question = await ctx.channel.send(embed=MAKE_EMBED(wallet))
    if len(wallet['wallet']) >= 1: await question.add_reaction('1️⃣')
    if len(wallet['wallet']) >= 2: await question.add_reaction('2️⃣')
    if len(wallet['wallet']) >= 3: await question.add_reaction('3️⃣')

    while True:
        def check(_reaction, _user):
            return str(_reaction) in ['1️⃣', '2️⃣', '3️⃣'] and _reaction.message.id == question.id and _user == ctx.author
        reaction, user = await bot.wait_for('reaction_add', check=check)

        if str(reaction) == '1️⃣' and len(wallet['wallet']) >= 1: idx = 0
        if str(reaction) == '2️⃣' and len(wallet['wallet']) >= 2: idx = 1
        if str(reaction) == '3️⃣' and len(wallet['wallet']) >= 3: idx = 2

        # 골드 차감
        w = wallet['wallet'][idx]
        price = Tool.getLatestPrice(w['stock'])['price']
        Tool.gainGold(did, w['bid'] * w['size'])
        Tool.gainGold(did, (price - w['bid']) * w['size'] * w['leverage'])

        #income = (w['bid'] * w['size']) + ((price - w['bid']) * w['size'] * w['leverage'])
        Tool.delStock(did, idx, price)

        # 지갑 업데이트
        stock = Tool.getStock(did)
        wallet = json.loads(stock['wallet'])
        await question.edit(embed=MAKE_EMBED(wallet))
        await question.clear_reactions()
        if len(wallet['wallet']) >= 1: await question.add_reaction('1️⃣')
        if len(wallet['wallet']) >= 2: await question.add_reaction('2️⃣')
        if len(wallet['wallet']) >= 3: await question.add_reaction('3️⃣')

async def 거래내역(ctx):
    await ctx.message.delete()
    did, name = ctx.message.author.id, ctx.message.author.display_name

    account = Tool.getAccount(did)
    if account is None:
        await ctx.channel.send(f"> {name}님은 선물 거래를 한 번도 하지 않았어요.")
        return

    stock = Tool.getStock(did)
    history = json.loads(stock['history'])

    embed = discord.Embed(title=f'{name}님의 선물 거래 내역을 보여드릴게요.')
    for h in history['history'][::-1]:
        name = f"> {h['date']}"
        value = f"종목 : {h['stock']}\n"
        value += f"유형 : { '매도' if h['leverage'] > 0 else '매수' }\n"
        value += f"주문가 : {format(h['bid'], ',')}골드\n"
        value += f"수량 : {format(h['size'] * abs(h['leverage']), ',')}개\n"
        value += f"실현 이익 : {format(h['income'], ',')}골드\n"
        embed.add_field(name=name, value=value)
    await ctx.channel.send(embed=embed)

async def 파산(bot, ctx):
    await ctx.message.delete()
    did, name = ctx.message.author.id, ctx.message.author.display_name

    account = Tool.getAccount(did)
    if account is None:
        await ctx.channel.send(f"> {name}님은 선물 거래를 한 번도 하지 않았어요.")
        return

    embed = discord.Embed(title=f"{name}님의 파산 신청")
    embed.add_field(name='> 신중하게 생각해주세요.',
                    value='''현재 보유 중인 골드와 포지션들이 모두 사라지고 절대 복구할 수 없어요.
                    또한 파산 신청한 날을 포함한 3일 동안은 선물 거래를 할 수 없어요.
                    이러한 내용을 확인하고 파산에 동의한다면 ✅ 이모지를 눌러주세요.
                    ''')
    question = await ctx.channel.send(embed=embed)
    await question.add_reaction('✅')

    def check(_reaction, _user):
        return str(_reaction) == '✅' and _reaction.message.id == question.id and _user == ctx.author
    reaction, user = await bot.wait_for('reaction_add', check=check)

    allowDate = datetime.now() + timedelta(days=3)
    allowDate = allowDate.strftime('%Y-%m-%d')
    Tool.setLiquidate(did, allowDate)

    await question.clear_reactions()
    await question.edit(context=f"> {name}님의 파산 신청이 완료되었어요.\n> {allowDate}부터 선물 거래를 다시 할 수 있어요.", embed=None)

def updateMarketPrices():
    import threading

    def target():
        # 시세 최신화
        for itemName in ['아이올라이트', '시간의 결정', '고대 지혜의 잔해',
                         '힘의 정수 1개 상자', '무색 큐브 조각', '모순의 결정체']:
            auction = DNFAPI.getItemAuction(itemName)
            p, c = 0, 0
            for i in auction:
                p += i['price']
                c += i['count']
            price = p // c
            Tool.updateAuctionPrice(itemName, price)

        # 청산 체크
        stocks = Tool.getStocks()
        for stock in stocks:
            wallet = json.loads(stock['wallet'])
            for idx, w in enumerate(wallet['wallet']):
                price = Tool.getLatestPrice(w['stock'])['price']
                if  (w['leverage'] > 0 and price <= w['margin']) or \
                    (w['leverage'] < 0 and price >= w['margin']):
                    Tool.delStock(stock['did'], idx, w['bid'])

    t = threading.Thread(target=target)
    t.start()
