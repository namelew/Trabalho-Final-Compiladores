from abc import abstractclassmethod

class Table:
    def __init__(self) -> None:
        pass
    @abstractclassmethod
    def Build(self):
        pass
    @abstractclassmethod
    def Action(self, row:str|int, collumn:str) -> str:
        pass

class LR(Table):
    def __init__(self) -> None:
        pass