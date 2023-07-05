from parser.PushownAutomaton import LR,PushdownAutomaton
from utils.SimbolTable import SimbolTable
from parser.Table import LRTable

class Parser:
    def __init__(self, tape:list[str], simbolTable:SimbolTable) -> None:
        self.tablefile = "./input/parser_table.xml"
        self.automato:PushdownAutomaton = LR(LRTable(self.tablefile), tape, simbolTable)