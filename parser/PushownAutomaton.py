from abc import abstractclassmethod
from utils.SimbolTable import SimbolTable
from parser.Table import Table,LRTable

class PushdownAutomaton:
    def __init__(self, table:Table, tape:list[str], simbolTable:SimbolTable) -> None:
        self.table:Table = table
        self.tape:list[str] = tape
        self.simbolTable:SimbolTable = simbolTable
        self.table.Build()
    @abstractclassmethod
    def Recognize(self) -> SimbolTable:
        pass
    @abstractclassmethod
    def jump(self):
        pass
    @abstractclassmethod
    def enqueue(self):
        pass
    @abstractclassmethod
    def reduce(self):
        pass

class LR(PushdownAutomaton):
    def __init__(self, table:LRTable, tape:list[str], simbolTable:SimbolTable) -> None:
        super().__init__(table, tape, simbolTable)
    def Recognize(self) -> SimbolTable:
        pass
    def jump(self):
        pass
    def enqueue(self):
        pass
    def reduce(self):
        pass