expression = input("Wpisz wyrazenie arytmetyczne: ").strip().replace(" ", "")
allowed="0123456789.+*"
for char in expression:
    if char not in allowed:
        print("Niedozwolony znak:", char)
        exit()
if "+" in expression:
    result = sum(map(float, expression.split("+")))
elif "*" in expression:
    from math import prod
    result = prod(map(float, expression.split("*")))
else:
    result = float(expression)

print(result)
