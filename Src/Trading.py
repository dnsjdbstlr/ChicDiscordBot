import asyncio
import discord
import json
from datetime import datetime, date, timedelta
from Database import Tool
from Src import DNFAPI

async def 선물거래(ctx):
    await ctx.message.delete()
    did = ctx.author.id

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
    did, name = ctx.author.id, ctx.author.display_name
    message = await ctx.channel.send(f"> {name}님의 주문을 준비중이예요...")

    # account가 없을 경우
    if Tool.getAccount(did) is None:
        Tool.iniAccount(did)

    # stock이 없을 경우
    stock = Tool.getStock(did)
    if stock is None: Tool.iniStock(did)
    stock = Tool.getStock(did)

    # 3개의 포지션을 보유하고 있을 경우
    wallet = json.loads(stock['wallet'])
    if len(wallet['wallet']) >= 3:
        await message.edit(content=f"> {name}님은 이미 3개의 포지션을 보유하고 있어요.\n"
                                    '> 보유한 포지션을 종료한 후 다시 시도해주세요.')
        return

    # 거래 금지인 경우
    today = datetime.today()
    if date(today.year, today.month, today.day) < stock['allowDate']:
        await message.edit(content=f"> {name}님은 {stock['allowDate']}부터 선물거래가 가능해요.")
        return

    # 입력이 잘못됬을 경우
    if len(inputs) == 0:
        await message.edit(content='> `!주문 <종목> <레버리지>` 의 형태로 다시 시도해주세요.')
        return

    # 레버리지, 종목명
    try:
        stockName = ' '.join(inputs[:-1])
        leverage = int(inputs[-1])
    except ValueError:
        stockName = ' '.join(inputs)
        leverage = 1

    # 종목이 잘못됬을 경우
    if stockName not in ['아이올라이트', '시간의 결정', '고대 지혜의 잔해',
                         '힘의 정수 1개 상자', '무색 큐브 조각', '모순의 결정체']:
        await message.edit(content='> 다음 종목들에 대해서만 주문을 넣을 수 있어요.\n'
                                   '> `아이올라이트`, `시간의 결정`, `고대 지혜의 잔해`,\n'
                                   '> `힘의 정수 1개 상자`, `무색큐브조각`, `모순의 결정체`')
        return

    # 레버리지가 잘못됬을 경우
    if leverage == 0 or abs(leverage) > 50:
        await message.edit(content='> 레버리지는 -50 ~ 50까지만 가능해요.\n'
                                   '> 레버리지를 다시 정해서 시도해주세요.')
        return

    # 데이터 세팅
    item   = DNFAPI.getMostSimilarItem(stockName)
    lPrice = Tool.getLatestPrice(stockName)
    pPrice = Tool.getPrevPrice(stockName)
    gold   = Tool.getGold(did)
    margin = int(lPrice['price'] * (1 - (1 / leverage) ))

    # 등락률
    if pPrice is None:
        val_rate = '데이터 없음'
    else:
        rate = (lPrice['price'] / pPrice['price'] - 1) * 100
        val_rate = f"▼ {format(rate, '.2f')}%" if rate < 0 else f"▲ {format(rate, '.2f')}%"

    # 출력
    orderType = '매수(롱)' if leverage > 0 else '매도(숏)'
    embed = discord.Embed(title=f"{name}님의 {orderType} 주문",
                          description=f"아래의 내용을 확인하고 {'매수량' if leverage > 0 else '매도량'}을 적어주세요.\n"
                                      '10초안에 입력하지 않으면 자동으로 주문이 취소되요.')
    embed.set_thumbnail(url=DNFAPI.getItemImageUrl(item['itemId']))
    embed.add_field(name='> 종목명', value=stockName)
    embed.add_field(name='> 현재가', value=f"{format(lPrice['price'], ',')}골드")
    embed.add_field(name='> 등락률', value=val_rate)
    embed.add_field(name='> 레버리지', value=f"x{abs(leverage)}")
    embed.add_field(name='> 청산가', value=f"{format(margin, ',')}골드")
    embed.add_field(name='> 최대 사이즈', value=f"{format(gold // lPrice['price'], ',')}개")
    embed.set_footer(text=f"지갑 잔고 : {format(gold, ',')}골드")
    await message.edit(content=None, embed=embed)

    try:
        def check(_message):
            return ctx.channel.id == _message.channel.id and ctx.message.author == _message.author
        answer = await bot.wait_for('message', check=check, timeout=10)

        if not answer.content.isnumeric() or int(answer.content) <= 0 or int(answer.content) > gold // lPrice['price']:
            await answer.delete()
            await message.edit(content=f"> {name}님의 {orderType} 주문이 취소되었어요.\n"
                                        f"> 입력이 잘못되었어요. 1 ~ {format(gold // lPrice['price'], ',')}의 숫자만 입력해야해요.", embed=None)
            return
        
        # 골드 차감
        Tool.addStock(did, {
            'stock'     : stockName,
            'leverage'  : leverage,
            'size'      : int(answer.content),
            'bid'       : lPrice['price'],
            'margin'    : margin
        })
        Tool.gainGold(did, -int(answer.content) * lPrice['price'])
        
        # 출력
        await answer.delete()
        embed = discord.Embed(title=f"{name}님의 {orderType} 주문",
                              description='주문이 성공적으로 체결됬습니다. 아래 내용을 확인해주세요.')
        embed.add_field(name='> 종목명', value=stockName)
        embed.add_field(name='> 사이즈', value=f"{answer.content}개")
        embed.add_field(name='> 레버리지', value=f"x{abs(leverage)}")
        embed.add_field(name='> 체결가격', value=f"{format(lPrice['price'], ',')}골드")
        embed.add_field(name='> 청산가격', value=f"{format(margin, ',')}골드")
        embed.set_thumbnail(url=DNFAPI.getItemImageUrl(item['itemId']))
        await message.edit(embed=embed)

    except asyncio.TimeoutError:
        await message.edit(content=f"> {name}님의 {orderType} 주문이 취소되었어요.\n"
                                    f"> 10초안에 {'매수량' if leverage > 0 else '매도량'}을 입력하지 않아서 자동으로 취소되었어요.", embed=None)
        return
    except Exception as e:
        await message.edit(content=f"> {name}님의 {orderType} 주문이 취소되었어요.\n > {e}")
        return

async def 포지션(bot, ctx):
    def MAKE_EMBED(eWallet):
        eDid, eName = ctx.message.author.id, ctx.message.author.display_name
        eEmbed = discord.Embed(title=f"{eName}님의 포지션",
                               description='종료하고 싶은 포지션이 있다면 해당 번호의 이모지를 눌러주세요.\n'
                                           '이모지를 누르면 즉시 해당 포지션을 종료합니다.')
        for ew in eWallet['wallet']:
            ePrice = Tool.getLatestPrice(ew['stock'])['price']
            eRate = (ePrice / ew['bid'] - 1) * 100 * ew['leverage']
            eRate = float(format(eRate, '.2f'))
            eRate = format(eRate, ',')

            eName = f"> {ew['stock']} x{abs(ew['leverage'])}{'롱' if ew['leverage'] > 0 else '숏'}"
            eValue = f"사이즈 : {format(ew['size'], ',')}개\n"
            eValue += f"진입 가격 : {format(ew['bid'], ',')}골드\n"
            eValue += f"현재 가격 : {format(ePrice, ',')}골드\n"
            eValue += f"청산 가격 : {format(ew['margin'], ',')}골드\n"
            eValue += f"손익률 : ▲ {eRate}%" if float(eRate) >= 0 else f"▼ {eRate}%"
            eEmbed.add_field(name=eName, value=eValue)

        for i in range(len(eWallet['wallet']), 3):
            eEmbed.add_field(name=f"> 포지션{i + 1}", value='없음')

        eEmbed.set_footer(text=f"지갑 잔고 : {format(Tool.getGold(eDid), ',')}골드")
        return eEmbed

    await ctx.message.delete()
    did, name = ctx.author.id, ctx.author.display_name
    message = await ctx.channel.send(f"> {name}님의 포지션 정보를 불러오고 있어요...")

    # account가 없을 경우
    if Tool.getAccount(did) is None:
        Tool.iniAccount(did)

    # stock이 없을 경우
    stock = Tool.getStock(did)
    if stock is None: Tool.iniStock(did)
    stock = Tool.getStock(did)

    wallet = json.loads(stock['wallet'])
    embed = MAKE_EMBED(wallet)
    await message.edit(content=None, embed=embed)
    if len(wallet['wallet']) >= 1: await message.add_reaction('1️⃣')
    if len(wallet['wallet']) >= 2: await message.add_reaction('2️⃣')
    if len(wallet['wallet']) >= 3: await message.add_reaction('3️⃣')
    await message.add_reaction('🔄')

    while True:
        def check(_reaction, _user):
            return str(_reaction) in ['1️⃣', '2️⃣', '3️⃣', '🔄'] and _reaction.message.id == message.id and _user == ctx.author
        reaction, user = await bot.wait_for('reaction_add', check=check)

        if str(reaction) == '1️⃣' and len(wallet['wallet']) >= 1: idx = 0
        if str(reaction) == '2️⃣' and len(wallet['wallet']) >= 2: idx = 1
        if str(reaction) == '3️⃣' and len(wallet['wallet']) >= 3: idx = 2
        if str(reaction) == '🔄':
            # 로딩
            stock = Tool.getStock(did)
            wallet = json.loads(stock['wallet'])
            embed.set_footer(text='포지션 정보를 최신화 중이예요...')
            await message.edit(embed=embed)
            await message.clear_reactions()

            # 최신화
            embed = MAKE_EMBED(wallet)
            await message.edit(embed=embed)
            if len(wallet['wallet']) >= 1: await message.add_reaction('1️⃣')
            if len(wallet['wallet']) >= 2: await message.add_reaction('2️⃣')
            if len(wallet['wallet']) >= 3: await message.add_reaction('3️⃣')
            await message.add_reaction('🔄')
            continue

        # 포지션 종료 로딩
        w = wallet['wallet'][idx]
        embed.set_footer(text=f"{w['stock']} x{abs(w['leverage'])}{'롱' if w['leverage'] > 0 else '숏'} 포지션을 종료하는 중이예요...")
        await message.edit(embed=embed)
        await message.clear_reactions()

        # 골드 차감
        price = Tool.getLatestPrice(w['stock'])['price']
        Tool.gainGold(did, (w['bid'] * w['size']) + (price - w['bid']) * w['size'] * w['leverage'])
        Tool.delStock(did, idx, price)

        # 포지션 최신화 로딩
        stock = Tool.getStock(did)
        wallet = json.loads(stock['wallet'])
        embed.set_footer(text='포지션 정보를 최신화 중이예요...')
        await message.edit(embed=embed)

        # 출력
        embed = MAKE_EMBED(wallet)
        await message.edit(embed=embed)
        if len(wallet['wallet']) >= 1: await message.add_reaction('1️⃣')
        if len(wallet['wallet']) >= 2: await message.add_reaction('2️⃣')
        if len(wallet['wallet']) >= 3: await message.add_reaction('3️⃣')
        await message.add_reaction('🔄')

async def 거래내역(bot, ctx):
    def MAKE_EMBED():
        eName = ctx.author.display_name
        eHistory = json.loads(stock['history'])
        eProfit = 0

        eEmbed = discord.Embed(title=f'{eName}님의 거래 내역을 보여드릴게요.')
        for eh in eHistory['history'][::-1]:
            eProfit += eh['income']

            eName = f"> {eh['date']}"
            eValue = f"종목 : {eh['stock']}\n"
            eValue += f"유형 : {'매수' if eh['leverage'] > 0 else '매도'}\n"
            eValue += f"주문가 : {format(eh['bid'], ',')}골드\n"
            eValue += f"수량 : {format(eh['size'] * abs(eh['leverage']), ',')}개\n"
            eValue += f"실현 이익 : {format(eh['income'], ',')}골드\n"
            eEmbed.add_field(name=eName, value=eValue)
        eEmbed.set_footer(text=f"총 손익 : {format(eProfit, ',')}골드")
        return eEmbed

    await ctx.message.delete()
    did, name = ctx.author.id, ctx.author.display_name

    # account, stock이 없을 경우
    account = Tool.getAccount(did)
    stock = Tool.getStock(did)
    if account is None or stock is None:
        await ctx.channel.send(f"> {name}님은 선물 거래를 한 번도 하지 않았어요.")
        return

    embed = MAKE_EMBED()
    message = await ctx.channel.send(embed=embed)
    await message.add_reaction('🔄')

    while True:
        def check(_reaction, _user):
            return str(_reaction) == '🔄' and _reaction.message.id == message.id and _user == ctx.author
        reaction, user = await bot.wait_for('reaction_add', check=check)

        embed.set_footer(text='거래 내역을 최신화 중이예요...')
        await message.edit(embed=embed)
        await message.clear_reactions()

        embed = MAKE_EMBED()
        await message.edit(embed=embed)
        await message.add_reaction('🔄')

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

async def 골드랭킹(bot, ctx):
    def MAKE_EMBED(eAccounts, ePage):
        eData = []      

        for eAccount in eAccounts:
            eStock = Tool.getStock(eAccount['did'])
            eGold = Tool.getGold(eAccount['did'])
            if eStock is None:
                eData.append({
                    'did' : eAccount['did'],
                    'sum' : eGold,
                    'gold' : eGold,
                    'evaluation' : 0,
                    'stocks' : [],
                    'liquidate' : 0
                })
            else:
                eEvaluation = 0
                eWallet = json.loads(eStock['wallet'])
                for idx, w in enumerate(eWallet['wallet']):
                    ePrice = Tool.getLatestPrice(w['stock'])['price']
                    eEvaluation += (w['bid'] * w['size']) + ((ePrice - w['bid']) * w['size'] * w['leverage'])

                eData.append({
                    'did': eStock['did'],
                    'sum': eGold + eEvaluation,
                    'gold': eGold,
                    'evaluation': eEvaluation,
                    'stocks': [ew['stock'] for ew in eWallet['wallet']],
                    'liquidate': eStock['liquidate']
                })

        eData.sort(key=lambda x: x['sum'], reverse=True)
        eData = eData[ePage * 15:ePage * 15 + 15]
        
        # 출력
        eEmbed = discord.Embed(title='보유금과 평가금의 합을 기준으로한 랭킹을 보여드릴게요.')
        for idx, i in enumerate(eData):
            eName = f"> {idx + 1}등"
            if i['did'] == str(ctx.author.id):
                eName += f"({ctx.author.display_name}님)"
            eName += f"> {format(i['sum'], ',')}골드"
            eValue = f"보유금 : {format(i['gold'], ',')}골드\n" \
                     f"평가금 : {format(i['evaluation'], ',')}골드\n" \
                     f"보유 종목 : {', '.join(i['stocks']) if i['stocks'] else '없음'}\n" \
                     f"파산 횟수 : {format(i['liquidate'], ',')}회"
            eEmbed.add_field(name=eName, value=eValue)
        eEmbed.set_footer(text=f"{ePage + 1}페이지 / {(len(eAccounts) - 1) // 15 + 1}페이지")
        return eEmbed

    await ctx.message.delete()
    message = await ctx.channel.send('> 골드 랭킹 데이터를 불러오고 있어요...')

    accounts = Tool.getAccounts()
    embed = MAKE_EMBED(accounts, 0)
    await message.edit(embed=embed, content=None)
    if len(accounts) > 15: await message.add_reaction('▶️')

    page = 0
    while len(accounts) > 15:
        try:
            def check(_reaction, _user):
                return str(_reaction) in ['◀️', '▶️'] and _user == ctx.author and _reaction.message.id == message.id
            reaction, user = await bot.wait_for('reaction_add', check=check)

            if str(reaction) == '◀️' and page > 0:
                page -= 1
            if str(reaction) == '▶️' and page < (len(accounts) - 1) // 15:
                page += 1

            embed = MAKE_EMBED(accounts, page)
            await message.edit(embed=embed)
            await message.clear_reactions()
            if page > 0:
                await message.add_reaction('◀️')
            if page < (len(accounts) - 1) // 15:
                await message.add_reaction('▶️')

        except Exception as e:
            await message.edit(content=f"> 오류가 발생했습니다.\n> {e}", embed=None)
            return

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
                    Tool.delStock(stock['did'], idx, w['margin'])

    t = threading.Thread(target=target)
    t.start()
