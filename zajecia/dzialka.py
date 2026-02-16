import matplotlib.pyplot as plt

# Dane wejściowe
x = list(map(float, input("Podaj współrzędne x: ").split()))
y = list(map(float, input("Podaj współrzędne y: ").split()))

# Sprawdzenie poprawności
if len(x) != len(y):
    raise ValueError("Liczba współrzędnych x i y musi być taka sama")

# Wyznaczenie granic
xmin, xmax = min(x), max(x)
ymin, ymax = min(y), max(y)

# Bok kwadratu
side = max(xmax - xmin, ymax - ymin)

# Współrzędne działki
x1 = xmin
y1 = ymax
x2 = xmin + side
y2 = ymax - side

print("\nWspółrzędne działki:")
print(f"x1 = {x1}, y1 = {y1}")
print(f"x2 = {x2}, y2 = {y2}")

# Rysowanie wykresu
plt.figure(figsize=(6, 6))

# Drzewa
plt.scatter(x, y, color='green', label='Drzewa', zorder=3)

# Kwadrat
square_x = [x1, x2, x2, x1, x1]
square_y = [y1, y1, y2, y2, y1]
plt.plot(square_x, square_y, color='red', label='Działka')

# Opisy
plt.xlabel("Oś X")
plt.ylabel("Oś Y")
plt.title("Działka obejmująca wszystkie drzewa")
plt.legend()
plt.grid(True)
plt.axis('equal')

plt.show()
