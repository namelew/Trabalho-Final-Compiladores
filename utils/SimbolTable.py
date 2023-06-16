class SimbolTable:
    def __init__(self) -> None:
        self.data:list[dict] = []
    def add(self, reg:dict):
        self.data.append(reg)