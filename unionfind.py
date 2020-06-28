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
            if self.par[i] !=  i:
                cnt.add(self.par[i])
        return len(cnt) == 1
