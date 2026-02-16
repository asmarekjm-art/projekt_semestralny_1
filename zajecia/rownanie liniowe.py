import numpy as np

# Wczytanie danych
row1 = list(map(float, input().split()))
row2 = list(map(float, input().split()))

A = np.array([
    [row1[0], row1[1]],
    [row2[0], row2[1]]
])

b = np.array([row1[2], row2[2]])

# Rzędy macierzy
rank_A = np.linalg.matrix_rank(A)
rank_Ab = np.linalg.matrix_rank(np.column_stack((A, b)))

if rank_A == rank_Ab == 2:
    solution = np.linalg.solve(A, b)
    print(f"x = {solution[0]}")
    print(f"y = {solution[1]}")

elif rank_A == rank_Ab == 1:
    print("Nieskończenie wiele rozwiązań.")

else:
    print("Brak rozwiązań.")
