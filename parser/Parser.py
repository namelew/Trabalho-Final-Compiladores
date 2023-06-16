from parser.PushownAutomaton import PushdownAutomaton

class Parser:
    def __init__(self, automato:PushdownAutomaton) -> None:
        self.automato:PushdownAutomaton = automato