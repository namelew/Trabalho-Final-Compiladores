from utils.SimbolTable import SimbolTable
from parser.Table import LRTable,Table
from os import _exit

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
        tape[-1] = 'EOF'
        tape.reverse()
        tokenid, lastTokenid, tokenPosition = -1, 0, 0

        print(f"Stack: {self.stack}, Tape: {' '.join(tape)}")

        while tokenid != 0:
            token = tape.pop()
            next = False
            tokenid = self.table.simbols[token][0]
            while not next:
                try:
                    action = self.table.Action(self.stack[-1], token)

                    if action[0] == SHIFT:
                        print(f"SHIFT {tokenid}, {action[1]}", end=". ")
                        self.stack.extend([tokenid, action[1]])
                        next = True
                        print(f"Stack: {self.stack}, Tape: {' '.join(tape)}")
                    if action[0] == REDUCE:
                        print(f"REDUCE {tokenid} for production {action[1]}", end=". ")
                        #self.stack.append(tokenid)
                        production = self.table.productions[action[1]]
                        for _ in range(production[1] * 2):
                            self.stack.pop()
                        lastTokenid = tokenid
                        tokenid = production[0]
                        print(f"Stack: {self.stack}, Tape: {' '.join(tape)}")
                    if action[0] == GOTO:
                        print(f"GOTO {tokenid} {action[1]}", end=". ")
                        self.stack.extend([tokenid, action[1]])
                        tokenid = lastTokenid
                        print(f"Stack: {self.stack}, Tape: {' '.join(tape)}")
                    if action[0] == ACCEPT:
                        return simbolTable
                except KeyError:
                    print(f"Sintax error on line {simbolTable.data[tokenPosition]['line']}: '{' '.join([simbolTable.data[j]['literal'] for j in range(0, tokenPosition+1)])}'")
                    _exit(0)
            tokenPosition += 1