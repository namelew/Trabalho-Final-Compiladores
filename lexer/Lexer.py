from lexer.FiniteAutomaton import DeterministicFiniteAutomaton
from os import _exit

class Lexer:
    def __init__(self, tokenfile:str) -> None:
        self.automaton:DeterministicFiniteAutomaton = DeterministicFiniteAutomaton(tokenfile)
        self.automaton.Build()
    def Read(self, filename:str) -> tuple[list[str], list[list[dict]]]:
        tape:list[str] = []
        simbolTable:list[list[dict]] = []

        try:
            file = open(filename, "r")
        except Exception as err:
            print("Unable to open file. Cause: ", err)
            _exit(1)
        
        for line in file.readlines():
            stRow:list[dict] = []
            line = line.replace("\t", "")
            line = line.replace("\n", "")
            words = line.split(" ")
            tape.extend(self.recognize(words, stRow))
            simbolTable.append(stRow)
        
        return tape, simbolTable

    def recognize(self, source:list[str], simbolTableRow:list[dict]) -> list[str]:
        tape:list[str] = []
        for token in source:
            if token == '':
                continue

            simbolTableCell = {'literal':token}
            currentState = self.automaton.initialState
            for i in range(len(token)):
                if i == len(token) - 1:
                    simbolTableCell['token'] = self.automaton.states[currentState]['token']
                    tape.append(self.automaton.states[currentState]['token'])
                else:
                    if self.automaton.nextState(currentState, token[i]) != '':
                        currentState = self.automaton.nextState(currentState, token[i])
            simbolTableRow.append(simbolTableCell)
        return tape