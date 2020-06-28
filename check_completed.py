import unionfind as unf

def check_completed(now, prv, size):
    uf = unf.UnionFind(len(prv))
    for i in range(size):
        uf.unite(i, prv[i])
        uf.unite(i, now[i])
    return uf.one_roop()

def main():
    da1 = list(map(int,input().split()))
    da2 = list(map(int,input().split()))
    print(check_completed(da1, da2, len(da1)))

if __name__ == "__main__":
    main()