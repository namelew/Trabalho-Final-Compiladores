from FiniteAutomaton import DeterministicFiniteAutomaton

class Lexer:
    def __init__(self, tokenfile:str) -> None:
        self.automaton = DeterministicFiniteAutomaton(tokenfile)
        self.tape = []
        self.automaton.Build()
    def Recognize(self, source:list[str]) -> list:
        pass