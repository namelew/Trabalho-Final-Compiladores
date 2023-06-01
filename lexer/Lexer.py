from lexer.FiniteAutomaton import DeterministicFiniteAutomaton

class Lexer:
    def __init__(self, tokenfile:str) -> None:
        self.automaton:DeterministicFiniteAutomaton = DeterministicFiniteAutomaton(tokenfile)
        self.automaton.Build()
    def Recognize(self, source:list[str]) -> list[str]:
        tape:list[str] = []
        for token in source:
            currentState = self.automaton.initialState
            for char in token:
                if self.automaton.nextState(currentState, char) != '':
                    currentState = self.automaton.nextState(currentState, char)
                else:
                    print(self.automaton[currentState]['token'])
                    tape.append(self.automaton[currentState]['token'])
        return tape