from lexer.FiniteAutomaton import DeterministicFiniteAutomaton

class Lexer:
    def __init__(self, tokenfile:str) -> None:
        self.automaton:DeterministicFiniteAutomaton = DeterministicFiniteAutomaton(tokenfile)
        self.automaton.Build()
    def Recognize(self, source:list[str]) -> list[str]:
        tape:list[str] = []
        print(source)
        print(self.automaton.states)
        for token in source:
            currentState = self.automaton.initialState
            for i in range(len(token)):
                if i == len(token) - 1:
                    tape.append(self.automaton.states[currentState]['token'])
                else:
                    if self.automaton.nextState(currentState, token[i]) != '':
                        currentState = self.automaton.nextState(currentState, token[i])
        return tape