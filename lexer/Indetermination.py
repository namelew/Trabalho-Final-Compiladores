class Indetermination:
    def __init__(self) -> None:
        self.parent = 0
        self.simbol = ''
        self.states = []
    def isIndetermination(self) -> bool:
        return len(self.states) > 1
    def __str__(self) -> str:
        return f"{self.parent} {self.simbol} {self.states}"