class UnionFind:
    def __init__(self):
        self.parent = {}

    def find(self, x):
        if x not in self.parent:
            self.parent[x] = x
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # kompresja ścieżki
        return self.parent[x]

    def union(self, a, b):
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a != root_b:
            self.parent[root_b] = root_a


uf = UnionFind()

while True:
    try:
        line = input().strip()
    except EOFError:
        break

    if line == "koniec":
        break

    parts = line.split()

    if parts[0] == "dodaj":
        _, a, b = parts
        uf.union(a, b)

    elif parts[0] == "czy":
        _, a, b = parts
        print("tak" if uf.find(a) == uf.find(b) else "nie")
