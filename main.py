from collections import defaultdict

class Candidate:
    def __init__(self, _size):
        self.size = _size
        self.vrtc = [False for i in range(self.size+1)]
        self.hrzn = [False for i in range(self.size)]
        self.connect = [i for i in range(self.size+1)]
    def bitmask(self, n, ignore_loop):
        for i in range(self.size):
            if (n>>i)&1:
                if self.add_hrzn(i) and (not ignore_loop):
                    return False
        for i in range(1, self.size):
            if self.hrzn[i] and self.hrzn[i-1] and self.vrtc[i]:
                return False
        return True
    def add_hrzn(self, x):
        ret = self.connect[x] == x+1 and self.connect[x+1] == x
        self.hrzn[x] = True
        a, b = self.connect[x], self.connect[x+1]
        self.connect[x] = x
        self.connect[x+1] = x+1
        if not ret:
            self.connect[a] = b
            self.connect[b] = a
        return ret
    def reset_hrzn(self, prv):
        self.connect = list(prv.connect)
        for i in range(self.size):
            self.vrtc[i] = False
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
        self.ans = []
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
            now.bitmask(i, False)
            self.cand[-1][candDict(now)].add()
    def search_sub(self, column):
        self.cand.append(defaultdict(CandData))
        for k,v in self.cand[column].items():
            now = Candidate(self.w)
            now.connect = list(k.connect)
            now.add_vert()
            for j in range(2**self.w):
                if now.bitmask(j, column == self.h-1):
                    tmp = candDict(now)
                    self.cand[-1][tmp].add()
                    v.to.append(self.cand[-1][tmp])
                now.reset_hrzn(k)
    def recognize_ans(self):
        tmp = tuple([i for i in range(self.w+1)])
        for i in self.cand[-1].keys():
            if i.connect == tmp:
                print("solved!")
                print(self.cand[-1][i].cnt)
                # return True
        print("no solution")
        return False
    def recover(self):
        pass
    def __str__(self):
        ansList = []
        for i in range(self.h*2 + 1):
            now  = ""
            if i%2 == 0:
                for j in range(self.w):
                    if self.ans_hrzn[i//2][j]:
                        now = now + "-"
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
    with open("sample2.txt") as f:
        lines = f.read()
    sl = SlitherLink(lines)
    sl.solve()
    for i in range(len(sl.cand)):
        for j in sl.cand[i]:
            print(j, i)

if __name__ == "__main__":
    main()
