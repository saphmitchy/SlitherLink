from collections import defaultdict

class UnionFind: #UnionFind木
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
    def count_roop(self): #頂点の数が2個以上の独立集合の数を返す
        cnt = set()
        for i in range(self.size):
            if self.root(i) !=  i:
                cnt.add(self.par[i])
        return len(cnt)

class Candidate:#線の引き方を管理するクラス
    def __init__(self, _size):
        self.size = _size #横何マスか
        self.vrtc = [False for i in range(self.size+1)] #縦線の引き方True->線がある
        self.hrzn = [False for i in range(self.size)] #横線の引き方True->線がある
        self.connect = [i for i in range(self.size+1)] #接続の仕方を管理する
    def bitmask(self, n):#2進数でx桁目が1ならself.hrzn[x-1]はTrue
        for i in range(self.size):
            if (n>>i)&1:
                self.add_hrzn(i)
    def add_hrzn(self, x):#横線を引くことでの接続の仕方を変更、connectをうまく書き換える
        self.hrzn[x] = True
        a, b = self.connect[x], self.connect[x+1]
        if a == x+1 and b == x:
            self.connect[x], self.connect[x+1] = b,a
            return
        self.connect[x] = x
        self.connect[x+1] = x+1
        self.connect[a] = b
        self.connect[b] = a
    def check_trns(self, prv):#線の枝分かれ、行き止まりがないか(後に縦線を追加するので3つ線が集まってないか見るだけでOK)
        for i in range(1, self.size):
            if self.vrtc[i] and prv.hrzn[i-1] and prv.hrzn[i]:
                return False
        return True
    def check_num(self, prv, k, nums): #数字の書かれたマスの周りの線の本数はあってるか
        for i in range(self.size):
            cnt = [prv.hrzn[i], k.hrzn[i], self.vrtc[i], self.vrtc[i+1]].count(True)
            if cnt != nums[i] and nums[i] != -1:
                return False
        return True
    def check_closed(self, prv):#線が閉じているか
        return self.count_pair(prv) == 0
    def count_pair(self, prv):#行き止まりになってるような場所の数
        cnt = 0
        for i in range(self.size+1):
            if (self.connect[i]==i)^(prv.connect[i]==i):
                cnt += 1
        return cnt
    def count_roop(self, prv):#頂点の数が2個以上の独立集合の数をUnionFind木を使って調べる。
        uf = UnionFind(self.size+1)
        for i in range(self.size+1):
            uf.unite(i, self.connect[i])
            uf.unite(i, prv.connect[i])
        return uf.count_roop()
    def check_completed(self, prv):#一つのループになっているか
        return self.count_roop(prv) == 1
    def check_roop(self, prv):#独立集合の数と線の行き止まりの数が一致しているか
        return self.count_pair(prv)//2 == self.count_roop(prv)
    def merge(self, prv):#横線を加える
        for i in range(self.size):
            if prv.hrzn[i]:
                self.add_hrzn(i)
    def reset_hrzn(self, prv):#状態のリセット
        self.connect = list(prv.connect)
        for i in range(self.size):
            self.hrzn[i] = False
    def add_vert(self):#縦線を加える
        for i in range(self.size+1):
            if self.connect[i] != i:
                self.vrtc[i] = True
    def __str__(self):
        return str(self.connect)+str(self.vrtc)+str(self.hrzn)+str(self.__hash__())

class CandDict: #リストのままだと辞書がうまく動かないことがあったのですべてタプルにしてから辞書に追加する
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

class CandData:#辞書のValues部分
    def __init__(self):
        self.cnt = 0 #その状態になるのが何通りか
        self.to = [] #どの状態へと遷移しうるか
    def add(self,prv):
        self.cnt += prv.cnt

class SlitherLink:
    def __init__(self, s):
        lines = s.split("\n")
        self.h, self.w = len(lines), len(lines[0]) #パズルの縦横の長さ
        self.data = [[-1 if lines[i][j] == "*" else int(lines[i][j]) for j in range(self.w)] for i in range(self.h)] #書き込まれた数字。無記入なら-1
        self.ans_vrtc = [[False for j in range(self.w + 1)] for i in range(self.h)] #縦線の管理
        self.ans_hrzn = [[False for j in range(self.w)] for i in range(self.h + 1)] #横線の管理
        self.cand = [] #探索中の頂点を管理
        self.ans = defaultdict(lambda : CandData()) #探索が終了し答えであるものを管理
        self.nonum_row = 0 #1以上の数字が書いてない最上行
        for i in range(self.h-1, -1, -1):
            if self.data[i].count(-1) + self.data[i].count(0) != self.w:
                self.nonum_row = i
                break
    def solve(self): #パズルを解く
        self.search() #解の探索
        if not self.recognize_ans(): #解が存在するか
            return
        self.recover() #解の復元
    def search(self):
        self.search_init() #最上行の線の引き方の列挙
        for column in range(self.h): #一行ずつ探索していく
            self.search_sub(column)
    def search_init(self):
        self.cand.append(defaultdict(CandData))
        for i in range(2**self.w): #2進数を利用して線の引き方を列挙する
            now = Candidate(self.w)
            now.bitmask(i)
            self.cand[-1][CandDict(now)].cnt = 1
    def search_sub(self, column):
        self.cand.append(defaultdict(CandData))
        for k,v in self.cand[column].items(): #直近の列で出た候補を全探索
            now = Candidate(self.w)
            now.connect = list(k.connect)#nowに一つ前の横線とつながり方をコピーする。
            now.add_vert() #このとき縦線の引き方は自然と確定する。
            for hrzn in self.cand[0]: #nowについて横線の引き方をぜんぶ試す。横線の引き方の列挙には最上行の線の引き方を利用。
                if now.check_trns(hrzn) and now.check_num(hrzn, k, self.data[column]): #線の分岐、本数のチェック
                    if now.check_closed(hrzn) and now.count_roop(hrzn) != 0: #線が閉じているか、独立集合ができているか(線を一本も引いていない状態をはじく)
                        if now.check_completed(hrzn) and self.can_end(hrzn, column): #一つのループか、今より下の行の数字との整合がとれているか
                            now.merge(hrzn) #nowに横線を追加
                            tmp = CandDict(now) #タプルにする
                            self.ans[tmp].to.append(column) #何行目かをメモしておく
                            self.ans[tmp].add(v) #解の個数のカウント
                            v.to.append(tmp) #辺を張る
                            now.reset_hrzn(k) #nowを横線を追加する前の状態に

                    else:
                        if now.check_roop(hrzn): #閉じたループがないかを調べる
                            now.merge(hrzn) #基本的に上と同様
                            tmp = CandDict(now)
                            self.cand[-1][tmp].add(v)
                            v.to.append(tmp)
                            now.reset_hrzn(k)
    def can_end(self, prv, column): #今見ている列より下と整合性がとれているか
        if self.nonum_row > column: #下の方に数字はないか
            return False
        elif column == self.h-1: #今が最下段ならOK
            return True
        for i in range(self.w): #直下の数字と整合性が取れているか
            if prv.hrzn[i]: #線があるなら0か無記入
                if self.data[column+1][i] != 1 and self.data[column+1][i] != -1:
                    return False
            else: #線がないなら無記入
                if self.data[column+1][i] > 0:
                    return False
        return True
    def recognize_ans(self): #解の個数
        if len(self.ans) > 0:
            ans_cnt = 0
            for i in self.ans.values(): #ansに入っているものをすべてカウント
                ans_cnt += i.cnt
            print(str(ans_cnt)+" solutions!")
            return True
        else:
            print("no solution")
            return False
    def recover(self): #解の復元
        prv = list(self.ans.keys())[0] #適当に一個取り出す
        nowrow = self.ans[prv].to[0]
        self.make_hrzn(prv, nowrow+1) #横線の構築
        while nowrow >= 0:
            self.make_vrtc(prv, nowrow) #縦線の構築
            prv = self.get_next(prv, nowrow) #一つ上の行をとってくる
            self.make_hrzn(prv, nowrow) #横線の構築
            nowrow-=1
    def make_hrzn(self, prv, nowrow): #横線の構築
        for i in range(self.w):
            if prv.hrzn[i]:
                self.ans_hrzn[nowrow][i] = True
    def make_vrtc(self, prv, nowrow): #縦線の構築
        for i in range(self.w + 1):
            if prv.vrtc[i]:
                self.ans_vrtc[nowrow][i] = True
    def get_next(self, prv, nowrow): #一つ下に行くものを一つとってくる
        for k,v in self.cand[nowrow].items():
            for j in v.to:
                if j == prv:
                    return k
    def valify(self): #解が正しいか
        if self.one_roop() and self.satisfy_num():
            print("Accepted!")
        else:
            print("Wrong Answer")
    def one_roop(self): #全体で一つのループか
        uf = UnionFind((self.w+1)*(self.h+1))
        cnt = [[0 for i in range(self.h+1)] for j in range(self.w+1)]
        for i in range(self.h+1):
            for j in range(self.w):
                if self.ans_hrzn[i][j]:
                    uf.unite((self.w+1)*i+j, (self.w+1)*i+j+1)
                    cnt[i][j] += 1
                    cnt[i][j+1] += 1
        for i in range(self.h):
            for j in range(self.w+1):
                if self.ans_vrtc[i][j]:
                    uf.unite((self.w+1)*i+j, (self.w+1)*(i+1)+j)
                    cnt[i][j] += 1
                    cnt[i+1][j] += 1
        for i in range(self.h+1): #全格子点について接続する線の本数は0か2
            for j in range(self.w+1):
                if cnt[i][j] != 2 and cnt[i][j] != 0:
                    return False
        return uf.count_roop() == 1 #格子点を頂点と見たときに要素が2以上の独立集合が一つ
    def satisfy_num(self): #書かれた数字と辺の本数が一致しているか
        for i in range(self.h):
            for j in range(self.w):
                if self.data[i][j] >= 0:
                    cnt = [self.ans_hrzn[i][j], self.ans_hrzn[i+1][j], self.ans_vrtc[i][j], self.ans_vrtc[i][j+1]].count(True)
                    if cnt != self.data[i][j]:
                        return False
        return True
    def __str__(self): #文字列に変換
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
    with open("./testcases/sample1.txt") as f:
        lines = f.read()
    sl = SlitherLink(lines)
    sl.solve()
    print(sl)
    sl.valify()

if __name__ == "__main__":
    main()
