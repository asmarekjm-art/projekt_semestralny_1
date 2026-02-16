import numpy as np
import matplotlib.pyplot as plt

# wczytanie danych
x = list(map(float, input("Podaj współrzędne x (oddzielone spacjami): ").split()))
y = list(map(float, input("Podaj współrzędne y (oddzielone spacjami): ").split()))

# sprawdzenie
if len(x) != len(y):
    print("Błąd: różna liczba punktów x i y!")
    exit()

x = np.array(x)
y = np.array(y)

# regresja liniowa
a, b = np.polyfit(x, y, 1)

# linia trendu
x_lin = np.linspace(min(x), max(x), 100)
y_lin = a * x_lin + b

# wykres
plt.scatter(x, y, color='red', label='Punkty')
plt.plot(x_lin, y_lin, color='green', label='Dopasowana prosta')

plt.xlabel('x')
plt.ylabel('y')
plt.title(f'y = {a:.3f}x + {b:.3f}')
plt.legend()
plt.grid(True)
plt.show()
