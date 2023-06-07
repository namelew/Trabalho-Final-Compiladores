from lexer.Lexer import Lexer

l = Lexer("./input/rules.in")
print(l.Recognize(["se", "aac", "faca", "c","senao", "aa"]))