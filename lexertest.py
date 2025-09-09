from lexer import tokenize

code = "if (x == 2) { x = x + 1 }"
print(tokenize(code))
