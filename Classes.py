class epicRank:
    def __init__(self):
        self.data = {}

    def add(self, chrId, info):
        self.update(info[1])
        self.data.update({chrId: info})

        def key(x): return x[1][4]
        self.data = dict(sorted(self.data.items(), key=key, reverse=True)[:15])

    def update(self, month):
        # 기존에 있던 데이터와 새로 들어온 데이터의 날짜가 다르다면
        # 기존 데이터 모두 삭제 후 새로 들어온 데이터 삽입
        for k in self.data.keys():
            if self.data[k][1] != month:
                self.data.clear()
            break

class setRank:
    def __init__(self):
        self.data = {}

    def add(self, chrId, info):
        self.data.update({chrId : info})

        def key(x): return x[1][2]
        self.data = dict(sorted(self.data.items(), key=key, reverse=True)[:15])