from utils.SimbolTable import SimbolTable
from parser.Table import LRTable,Table

TABLESOURCE = "./input/parser_table.xml"
class Parser:
    def __init__(self) -> None:
        self.initialState:int = 0
        self.stack:list[str|int] = []
        self.table:Table = LRTable(TABLESOURCE)
        self.table.Build()
    def Analyse(self, tape:list[str], simbolTable:SimbolTable) -> SimbolTable:
        ...