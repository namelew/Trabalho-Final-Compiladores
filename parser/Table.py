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

class LRTable(Table):
    def __init__(self, sourcefile:str) -> None:
        self.tablefile:str = sourcefile