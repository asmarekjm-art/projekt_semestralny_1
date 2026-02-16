from collections import defaultdict, deque

# ---------- pomocnicze ----------
def area(p):
    x1, y1, x2, y2 = p
    return abs(x2 - x1) * abs(y1 - y2)

def overlap(a1, a2, b1, b2):
    return min(a2, b2) > max(a1, b1)

def touch(p1, p2):
    x1, y1, x2, y2 = p1
    x3, y3, x4, y4 = p2

    # pionowe stykanie
    if x2 == x3 or x1 == x4:
        return overlap(y2, y1, y4, y3)

    # poziome stykanie
    if y2 == y3 or y1 == y4:
        return overlap(x1, x2, x3, x4)

    return False

# ---------- wczytanie ----------
with open("parcele.txt") as f:
    n = int(f.readline())
    parcels = [tuple(map(float, f.readline().split())) for _ in range(n)]

# ---------- budowa grafu ----------
graph = defaultdict(list)

for i in range(n):
    for j in range(i + 1, n):
        if touch(parcels[i], parcels[j]):
            graph[i].append(j)
            graph[j].append(i)

# ---------- spójne składowe ----------
visited = [False] * n
groups = []

for i in range(n):
    if not visited[i]:
        q = deque([i])
        visited[i] = True
        group = [i]

        while q:
            v = q.popleft()
            for u in graph[v]:
                if not visited[u]:
                    visited[u] = True
                    q.append(u)
                    group.append(u)

        groups.append(group)

# ---------- liczenie pól ----------
result = []
for g in groups:
    total_area = sum(area(parcels[i]) for i in g)
    result.append((sorted([i + 1 for i in g]), total_area))

# ---------- sortowanie ----------
result.sort(key=lambda x: x[1], reverse=True)

# ---------- zapis ----------
with open("zestawienie.txt", "w") as f:
    f.write("Zestawienie parceli:\n")
    for ids, a in result:
        f.write(f"{'+'.join(map(str, ids))}: pole = {a:.0f}\n")
