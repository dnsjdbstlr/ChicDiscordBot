import json

class epicRank:
    def __init__(self):
        self.data = {}
        try:
            with open('Data/epicRank.json', 'r') as f:
                self.data = json.load(f)
                print('기린랭킹을 성공적으로 불러왔습니다.')
        except:
            print('기존 기린랭킹 데이터가 없습니다.')

    def add(self, chrId, info):
        self.update(info['month'])
        self.data.update({chrId: info})

        def key(x): return x[1]['score']
        self.data = dict(sorted(self.data.items(), key=key, reverse=True)[:15])

        # 파일로 저장
        with open('Data/epicRank.json', 'w') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

    def update(self, month):
        # 기존에 있던 데이터와 새로 들어온 데이터의 날짜가 다르다면
        # 기존 데이터 모두 삭제 후 새로 들어온 데이터 삽입
        for k in self.data.keys():
            if self.data[k]['month'] != month:
                self.data.clear()
            break

class setRank:
    def __init__(self):
        self.data = {}
        try:
            with open('Data/setRank.json', 'r') as f:
                self.data = json.load(f)
                print('세팅랭킹을 성공적으로 불러왔습니다.')
        except:
            print('기존 세팅랭킹 데이터가 없습니다.')

    def add(self, chrId, info):
        self.data.update({chrId : info})

        def key(x): return x[1]['score']
        self.data = dict(sorted(self.data.items(), key=key, reverse=True)[:15])

        # 파일로 저장
        with open('Data/setRank.json', 'w') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

class itemAuctionPrice:
    def __init__(self):
        self.data = {}
        try:
            with open('Data/itemAuctionPrice.json', 'r') as f:
                self.data = json.load(f)
                print('아이템 시세를 성공적으로 불러왔습니다.')
        except:
            print('기존 아이템 시세 데이터가 없습니다.')

    def update(self):
        # 파일로 저장
        with open('Data/itemAuctionPrice.json', 'w') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

class cmdStatistics:
    def __init__(self):
        self.data = {
            '!도움말'   : 0,
            '!등급'     : 0,
            '!캐릭터'   : 0,
            '!장비'     : 0,
            '!세트'     : 0,
            '!획득에픽' : 0,
            #'!상세정보' : 0,
            '!기린랭킹' : 0,
            #'!세팅랭킹' : 0,
            '!청소'     : 0
        }

        try:
            with open('Data/cmdStatistics.json', 'r') as f:
                self.data = json.load(f)
                print('명령어 통계를 성공적으로 불러왔습니다.')
        except:
            print('기존 명령어 통계 데이터가 없습니다.')

    def update(self):
        # 파일로 저장
        with open('Data/cmdStatistics.json', 'w') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)