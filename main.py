from lexer.Lexer import Lexer
from parser.Parser import Parser

tape,simbolTable = Lexer().Read("exemplo1.txt")

p = Parser()

try:
    p.Analyse(tape,simbolTable)
except:
    print(p.table.simbols)