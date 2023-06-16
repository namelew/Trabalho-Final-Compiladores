from abc import abstractclassmethod
from utils.SimbolTable import SimbolTable
from parser.Table import Table

class PushdownAutomaton:
    def __init__(self, table:Table, tape:list[str], simbolTable:SimbolTable) -> None:
        self.table = table
        self.tape = tape
        self.simbolTable = simbolTable
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
    def __init__(self) -> None:
        pass