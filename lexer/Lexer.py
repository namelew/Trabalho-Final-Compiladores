from lexer.FiniteAutomaton import DeterministicFiniteAutomaton
from utils.SimbolTable import SimbolTable
from os import _exit

class Lexer:
    def __init__(self, tokenfile:str) -> None:
        self.automaton:DeterministicFiniteAutomaton = DeterministicFiniteAutomaton(tokenfile)
        self.automaton.Build()
    def Read(self, filename:str) -> tuple[list[str], SimbolTable]:
        tape:list[str] = []
        simbolTable:SimbolTable = SimbolTable()

        try:
            file = open(filename, "r")
        except Exception as err:
            print("Unable to open file. Cause: ", err)
            _exit(1)
        
        i = 0
        for line in file.readlines():
            line = line.replace("\t", "")
            line = line.replace("\n", "")
            words = line.split(" ")
            tape.extend(self.recognize(words, simbolTable, i + 1))
            i += 1
        
        for reg in simbolTable.data:
            if reg['token'] == "error":
                print(f"Error léxico na linha {reg['line']}: {reg['literal']}")
                _exit(1)
        
        return tape, simbolTable

    def recognize(self, source:list[str], simbolTable:SimbolTable, line:int) -> list[str]:
        tape:list[str] = []
        for token in source:
            if token == '':
                continue

            simbolTableCell = {'literal':token, 'line': line}
            currentState = self.automaton.initialState
            for i in range(len(token) - 1 if  len(token) > 1 else 1):
                if self.automaton.nextState(currentState, token[i]) != '':
                    currentState = self.automaton.nextState(currentState, token[i])
            stateID = self.automaton.states[currentState]['token'] if "token" in self.automaton.states[currentState] else "error" 
            simbolTableCell['token'] = stateID
            tape.append(stateID)
            simbolTable.add(simbolTableCell)
        return tape