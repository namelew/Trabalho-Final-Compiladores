from abc import abstractclassmethod
import xml.etree.ElementTree as ET

class Table:
    def __init__(self) -> None:
        self.simbols:dict[list[str,int]] =  dict()
        self.productions:dict[list[int,int]] =  dict()
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
    def Build(self):
        tree = ET.parse(self.tablefile)
        for node in tree.findall('.//m_Symbol/Symbol'):
            self.simbols[int(node.attrib['Index'])] = [node.attrib['Name'], int(node.attrib['Type'])]

        for node in tree.findall('.//m_Production/Production'):
            self.productions[int(node.attrib['Index'])] = [int(node.attrib['NonTerminalIndex']), int(node.attrib['SymbolCount'])]
        
        print(self.simbols)
        print(self.productions)