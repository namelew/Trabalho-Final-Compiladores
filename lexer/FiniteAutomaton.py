import re
from lexer.Indetermination import Indetermination

class FiniteAutomaton:
    def __init__(self, sourcefile:str):
        self.sourcefile:str = sourcefile
        self.nRules:int = 0
        self.initialState:str = '<0>'
        self.rules:list[list[str]] = []
        self.states:dict = {}
        self.keywords:set[int] = set()
        self.terminals:set[int] = set()
        self.unreacheble:set[int] = set()
        self.dead:set[int] = set()
        self.alphabet:tuple[str] = tuple()
    def Build(self):
        self.loadFile()
        self.createStates()
    def createStates(self):
        newInitial = self.nRules - 1

        # gera estados a partir das regras
        for i in range(self.nRules):
            # ignora inalcançaveis e mortos
            if i in self.unreacheble or i in self.dead:
                continue
            # atualiza estado inicial
            if i < newInitial:
                newInitial = i
            # cria novo estado
            self.states[f'<{i}>'] = {}
            for char in self.alphabet:
                for production in self.rules[i]:
                    # utiliza expressão regular para mortar o par (simbolo, Estado)
                    matched = re.match(f'{char}(<\d+>)|^{char}$', production)
                    if matched:
                        if char not in self.states[f'<{i}>'] or self.states[f'<{i}>'][char] == '':
                            self.states[f'<{i}>'][char] = matched.group(1) if re.match(f'{char}<\d+>', matched.group(0)) else ''
                # adiciona transições para o estado de erro
                if char not in self.states[f'<{i}>']:
                    self.states[f'<{i}>'][char] = '<ERROR>'
            if i in self.terminals:
                self.states[f'<{i}>']["token"] = "var" if i not in self.keywords else f"{i}"
        self.initialState = f'<{newInitial}>'
        self.states['<ERROR>'] = {}
        for char in self.alphabet:
            self.states['<ERROR>'][char] = ''
            self.states['<ERROR>']["token"] = 'error'
    def loadFile(self):
        file = open(self.sourcefile)

        vars = []
        words = []

        # separa gramáticas de palavras reservadas
        for line in file.readlines():
            if re.search("^<\w>(.*)::=(.*)", line):
                vars.append(line.replace('\n', '').replace(' ', ''))
            else:
                words.append(line.replace('\n', '').replace(' ', ''))

        file.close()

        # remapeia os estados para a posição deles na lista
        for i in range(len(vars)):
            state = vars[i].split('::=')[0]
            for j in range(len(vars)):
                new = "<"+str(self.nRules)+">"
                vars[j] = re.sub(state, new, vars[j])
            self.nRules+=1
        
        # cria sub lista de produções e mapeia terminais
        for var in vars:
            productions = var.split('::=')[1]
            self.rules.append(productions.split('|'))
            if re.search('epsi$|\w$|\w\|', productions):
                self.terminals.add(len(self.rules) - 1)

        # transforma palavras reservadas em transições
        for word in words:
            nchars = len(word)
            for j in range(nchars):
                if j == 0:
                    self.rules[0].append(word[j]+f"<{self.nRules}>")
                    self.nRules += 1
                elif j == nchars - 1:
                    self.rules.append([word[j]])
                    self.terminals.add(self.nRules - 1)
                    self.keywords.add(self.nRules - 1)
                else:
                    self.rules.append([word[j]+f"<{self.nRules}>"])
                    self.nRules += 1
        # cria alfabeto
        characters = set()
        for state in self.rules:
            for transitions in state:
                matched = re.match('^\w|^epsi', transitions)
                if matched:
                    characters.add(matched.group(0))
        self.alphabet = tuple(sorted(list(characters)))
    def nextState(self, currentState:str, simbol:str) -> str:
        return self.states[currentState][simbol]

class DeterministicFiniteAutomaton(FiniteAutomaton):
    def __init__(self, sourcefile:str):
        super().__init__(sourcefile)
    def Build(self):
        self.loadFile()
        self.__determinate()
        self.createStates()
    def __getindeterminations(self) -> list:
        # lista de indeterminizações
        inds = []

        for i in range(len(self.rules)):
            for char in self.alphabet:
                ind = Indetermination()
                temp = set()

                for j in range(len(self.rules[i])):
                    # utilizando expressão regular para encontrar interminizações
                    matched = re.match(f"{char}<(\d+)>", self.rules[i][j])
                    if matched:
                        ind.parent = i
                        ind.simbol = char
                        temp.add(int(matched.group(1)))
                ind.states.extend(temp)
                if ind.isIndetermination():
                    inds.append(ind)
        return inds
    def __solveindeterminations(self, inds:list[Indetermination], newRules:list[list[str]]) -> set[int]:
        reachbleRules = set()
        newStates = list()

        for ind in inds:
            new = ind.Solve(self.rules, newRules, self.nRules, reachbleRules, self.terminals, self.keywords)
            if len(new) < 1:
                break
            newRules.append(new)
            reachbleRules.add(self.nRules)
            newStates.append(self.nRules)
            self.nRules += 1
        
        for state in newStates:
            for ind in inds:
                prods = [f'{ind.simbol}<{si}>' for si in ind.states]
                if all(pd in newRules[state] for pd in prods):
                    newRules[state] = [elem for elem in newRules[state] if elem not in prods]
                    newRules[state].append(ind.solution)

        return reachbleRules
    def __determinate(self):
        rstates = set()
        inds = self.__getindeterminations()

        while len(inds) > 0:
            new = self.rules.copy()
            result = self.__solveindeterminations(inds, new)
            if len(result) > 0:
                rstates = rstates.union(result)
            self.rules = new.copy()
            inds = self.__getindeterminations()
        
        # listando estados alcançáveis pelos alcançáveis conhecidos
        for i in range(self.nRules):
            if i in rstates:
                for production in self.rules[i]:
                    matched = re.match(f'\w<(\d+)>', production)
                    if matched:
                        rstates.add(int(matched.group(1)))
        
        # criando conjunto de não alcançáveis
        self.unreacheble = set([i for i in range(self.nRules)]).difference(rstates)