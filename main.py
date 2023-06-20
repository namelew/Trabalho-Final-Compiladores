from lexer.Lexer import Lexer
from parser.Parser import Parser

tape,simbolTable = Lexer().Read("exemplo1.txt")

p = Parser(tape, simbolTable)