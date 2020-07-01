from collections import defaultdict

class UnionFind:
    def __init__(self, _size):
        self.size = _size
        self.par = [i for i in range(self.size)]
    def root(self,x):
        if self.par[x] == x:
            return x
        else:
            self.par[x] = self.root(self.par[x])
            return self.par[x]
    def unite(self, x, y):
        x = self.root(x)
        y = self.root(y)
        self.par[x] = y
    def one_roop(self):
        cnt = set()
        for i in range(self.size):
            if self.root(i) !=  i:
                cnt.add(self.par[i])
        return len(cnt) == 1

class Candidate:
    def __init__(self, _size):
        self.size = _size
        self.vrtc = [False for i in range(self.size+1)]
        self.hrzn = [False for i in range(self.size)]
        self.connect = [i for i in range(self.size+1)]
    def bitmask(self, n):
        for i in range(self.size):
            if (n>>i)&1:
                self.add_hrzn(i)
    def add_hrzn(self, x):
        self.hrzn[x] = True
        a, b = self.connect[x], self.connect[x+1]
        if a == x+1 and b == x:
            self.connect[x], self.connect[x+1] = b,a
            return
        self.connect[x] = x
        self.connect[x+1] = x+1
        self.connect[a] = b
        self.connect[b] = a
    def check_trns(self, prv):
        for i in range(1, self.size):
            if self.vrtc[i] and prv.hrzn[i-1] and prv.hrzn[i]:
                return False
        return True
    def check_num(self, prv, k, nums):
        for i in range(self.size):
            cnt = [prv.hrzn[i], k.hrzn[i], self.vrtc[i], self.vrtc[i+1]].count(True)
            if cnt != nums[i] and nums[i] != -1:
                return False
        return True
    def check_roop(self, prv):
        for i in range(self.size):
            if (self.connect[i]==i)^(prv.connect[i]==i):
                return False
        return True
    def check_completed(self, prv):
        uf = UnionFind(self.size+1)
        for i in range(self.size+1):
            uf.unite(i, self.connect[i])
            uf.unite(i, prv.connect[i])
        return uf.one_roop()
    def merge(self, prv):
        for i in range(self.size):
            if prv.hrzn[i]:
                self.add_hrzn(i)
    def reset_hrzn(self, prv):
        self.connect = list(prv.connect)
        for i in range(self.size):
            self.hrzn[i] = False
    def add_vert(self):
        for i in range(self.size+1):
            if self.connect[i] != i:
                self.vrtc[i] = True
    def __str__(self):
        return str(self.connect)+str(self.vrtc)+str(self.hrzn)+str(self.__hash__())

class candDict:
    def __init__(self, cand):
        self.size = cand.size
        self.vrtc = tuple(cand.vrtc)
        self.hrzn = tuple(cand.hrzn)
        self.connect = tuple(cand.connect)
    def __str__(self):
        return str(self.connect)+str(self.vrtc)+str(self.hrzn)+str(self.__hash__())
    def __eq__(self, other):
        return self.connect == other.connect and self.hrzn == other.hrzn
    def __hash__(self):
        return hash(self.connect)^hash(self.hrzn)

class CandData:
    def __init__(self):
        self.cnt = 0
        self.to = []
    def add(self):
        self.cnt += 1

class SlitherLink:
    def __init__(self, s):
        lines = s.split("\n")
        self.h, self.w = len(lines), len(lines[0])
        self.data = [[-1 if lines[i][j] == "*" else int(lines[i][j]) for j in range(self.w)] for i in range(self.h)]
        self.ans_vrtc = [[False for j in range(self.w + 1)] for i in range(self.h)]
        self.ans_hrzn = [[False for j in range(self.w)] for i in range(self.h + 1)]
        self.cand = []
        self.ans = defaultdict(lambda : [])
        self.nonum_row = 0
        for i in range(self.h-1, -1, -1):
            if self.data[i].count(-1) != self.w:
                self.nonum_row = i
                break
    def solve(self):
        self.search()
        if not self.recognize_ans():
            return
        self.recover()
    def search(self):
        self.search_init()
        for column in range(self.h):
            self.search_sub(column)
    def search_init(self):
        self.cand.append(defaultdict(CandData))
        for i in range(2**self.w):
            now = Candidate(self.w)
            now.bitmask(i)
            self.cand[-1][candDict(now)].add()
    def search_sub(self, column):
        self.cand.append(defaultdict(CandData))
        for k,v in self.cand[column].items():
            now = Candidate(self.w)
            now.connect = list(k.connect)
            now.add_vert()
            for hrzn in self.cand[0]:
                if now.check_trns(hrzn) and now.check_num(hrzn, k, self.data[column]):
                    if now.check_roop(hrzn):
                        if now.check_completed(hrzn) and self.nonum_row <= column:
                            now.merge(hrzn)
                            tmp = candDict(now)
                            self.ans[tmp].append(column)
                            v.to.append(tmp)
                    else:
                        now.merge(hrzn)
                        tmp = candDict(now)
                        self.cand[-1][tmp].add()
                        v.to.append(tmp)
                    now.reset_hrzn(k)
    def recognize_ans(self):
        if len(self.ans) > 0:
            print("solved!")
            return True
        else:
            print("no solution")
            return False
    def recover(self):
        prv = list(self.ans.keys())[0]
        prv.is_ans = True
        nowrow = self.ans[prv][0]
        self.make_hrzn(prv, nowrow+1)
        while nowrow >= 0:
            self.make_vrtc(prv, nowrow)
            prv = self.get_next(prv, nowrow)
            self.make_hrzn(prv, nowrow)
            nowrow-=1
    def make_hrzn(self, prv, nowrow):
        for i in range(self.w):
            if prv.hrzn[i]:
                self.ans_hrzn[nowrow][i] = True
    def get_next(self, prv, nowrow):
        for k,v in self.cand[nowrow].items():
            for j in v.to:
                if j == prv:
                    return k
    def make_vrtc(self, prv, nowrow):
        for i in range(self.w + 1):
            if prv.vrtc[i]:
                self.ans_vrtc[nowrow][i] = True
    def vailfy(self):
        if self.one_roop() and self.satisfy_num():
            print("Accepted!")
        else:
            print("Wrong Answer")
    def one_roop(self):
        uf = UnionFind((self.w+1)*(self.h+1))
        for i in range(self.h+1):
            for j in range(self.w):
                if self.ans_hrzn[i][j]:
                    uf.unite((self.w+1)*i+j, (self.w+1)*i+j+1)
        for i in range(self.h):
            for j in range(self.w+1):
                if self.ans_vrtc[i][j]:
                    uf.unite((self.w+1)*i+j, (self.w+1)*(i+1)+j)
        return uf.one_roop()
    def satisfy_num(self):
        for i in range(self.h):
            for j in range(self.w):
                if self.data[i][j] >= 0:
                    cnt = [self.ans_hrzn[i][j], self.ans_hrzn[i+1][j], self.ans_vrtc[i][j], self.ans_vrtc[i][j+1]].count(True)
                    if cnt != self.data[i][j]:
                        return False
        return True
    def __str__(self):
        ansList = []
        for i in range(self.h*2 + 1):
            now  = ""
            if i%2 == 0:
                now = " "
                for j in range(self.w):
                    if self.ans_hrzn[i//2][j]:
                        now = now + "_"
                    else:
                        now = now + " "
                    if j < self.w-1:
                        now = now + " "
            else:
                for j in range(self.w*2 + 1):
                    if j%2 == 0:
                        if self.ans_vrtc[i//2][j//2]:
                            now = now + "|"
                        else:
                            now = now + " "
                    else:
                        if self.data[i//2][j//2] == -1:
                            now = now + " "
                        else:
                            now = now + str(self.data[i//2][j//2])
            ansList.append(now)
        ansstr = ""
        for strs in ansList:
            ansstr = ansstr + strs + "\n"
        return ansstr

def main():
    with open("sample1.txt") as f:
        lines = f.read()
    sl = SlitherLink(lines)
    sl.solve()
    print(sl)
    sl.vailfy()
    # for i,j in sl.ans.items():
    #     print(i, j)
    # for i in range(len(sl.cand)):
    #     for j in sl.cand[i]:
    #         print(j, i)

if __name__ == "__main__":
    main()
