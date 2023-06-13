from lexer.Lexer import Lexer

l = Lexer("./input/rules.in")
tape, stable = l.Read("exemplo1.txt")
print(tape, stable)