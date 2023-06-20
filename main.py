from lexer.Lexer import Lexer

l = Lexer()
tape, stable = l.Read("exemplo1.txt")
print(tape, stable.data)