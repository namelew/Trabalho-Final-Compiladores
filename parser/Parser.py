from utils.SimbolTable import SimbolTable
from parser.Table import LRTable,Table

TABLESOURCE = "./input/parser_table.xml"
SHIFT = 1
REDUCE = 2
GOTO = 3
ACCEPT = 4
class Parser:
    def __init__(self) -> None:
        self.initialState:int = 0
        self.stack:list[str|int] = []
        self.table:Table = LRTable(TABLESOURCE)
        self.table.Build()
    def Analyse(self, tape:list[str], simbolTable:SimbolTable) -> SimbolTable:
        self.stack.append(self.initialState)

        for token in tape:
            action = self.table.Action(self.stack[-1], int(token))
            
            if action[0] == SHIFT:
                pass
            if action[0] == REDUCE:
                pass
            if action[0] == GOTO:
                pass
            if action[0] == ACCEPT:
                pass