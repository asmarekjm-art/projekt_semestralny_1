import numpy as np

# Wczytanie wymiaru macierzy
N = int(input())

# Wczytanie macierzy A
A = []
for _ in range(N):
    A.append(list(map(int, input().split())))
A = np.array(A)

# Wczytanie macierzy B
B = []
for _ in range(N):
    B.append(list(map(int, input().split())))
B = np.array(B)

# Obliczenie komutatora [A, B] = AB - BA
commutator = A @ B - B @ A

# Sprawdzenie czy komutator jest zerowy
if np.all(commutator == 0):
    print("Komutator wynosi zero.")
else:
    for row in commutator:
        print(*row)
