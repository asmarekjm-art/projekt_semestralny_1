expr = input("Podaj wyrażenie: ")
expr = expr.replace(" ", "")
operators = "+-*/"

allowed = "0123456789+-*/"
if any(ch not in allowed for ch in expr):
    print("Błąd: wyrażenie zawiera niedozwolone znaki!")
    exit()

# znajdź operator1 i operator2
op1 = ""
op2 = ""
pos1 = -1
pos2 = -1

# znajdź pozycje operatorów
for i, ch in enumerate(expr):
    if ch in operators:
        if op1 == "":
            op1 = ch
            pos1 = i
        else:
            op2 = ch
            pos2 = i

# wyciągnij 3 liczby
a = float(expr[:pos1])
b = float(expr[pos1+1:pos2])
c = float(expr[pos2+1:])

# funkcja wykonująca działanie
def calc(x, op, y):
    if op == "+":
        return x + y
    if op == "-":
        return x - y
    if op == "*":
        return x * y
    if op == "/":
        if y == 0:
            print("Błąd: nie można dzielić przez 0!")
            exit()
        return x / y

# kolejność działań: * i / pierwsze
if op2 in "*/":
    # najpierw drugie działanie
    temp = calc(b, op2, c)
    result = calc(a, op1, temp)
else:
    # najpierw pierwsze działanie
    temp = calc(a, op1, b)
    result = calc(temp, op2, c)

print(result)
