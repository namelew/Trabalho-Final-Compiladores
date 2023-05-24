import re
from Indetermination import Indetermination

class FiniteAutomaton:
    def __init__(self, sourcefile:str):
        self.sourcefile = sourcefile
        self.nRules = 0
        self.rules = []
        self.states = {}
        self.terminals = set()
        self.unreacheble = set()
        self.dead = set()
        self.alphabet = tuple()
    def Build(self):
        self.loadRead()
        self.createStates()
        print(self.states)
    def createStates(self):
        for i in range(self.nRules):
            if i in self.unreacheble or i in self.dead:
                continue
            self.states[f'<{i}>'] = {}
            for char in self.alphabet:
                for production in self.rules[i]:
                    matched = re.match(f'{char}(<\d>)|^{char}$', production)
                    if matched:
                        if re.match(f'{char}<\d>', matched.group(0)):
                            self.states[f'<{i}>'][char] = matched.group(1)
                        elif re.match(f'^{char}$', matched.group(0)):
                            self.states[f'<{i}>'][char] = ''
                if char not in self.states[f'<{i}>']:
                    self.states[f'<{i}>'][char] = '<ERROR>'
        self.states['<ERROR>'] = {}
        for char in self.alphabet:
            self.states['<ERROR>'][char] = ''
    def loadRead(self):
        file = open(self.sourcefile)

        vars = []
        words = []

        for line in file.readlines():
            if re.search("^<\w>(.*)::=(.*)", line):
                vars.append(line.replace('\n', '').replace(' ', ''))
            else:
                words.append(line.replace('\n', '').replace(' ', ''))

        file.close()

        for i in range(len(vars)):
            state = vars[i].split('::=')[0]
            for j in range(len(vars)):
                new = "<"+str(self.nRules)+">"
                vars[j] = re.sub(state, new, vars[j])
            self.nRules+=1
        
        for var in vars:
            productions = var.split('::=')[1]
            self.rules.append(productions.split('|'))
            if re.search('epsi$|\w$|\w\|', productions):
                self.terminals.add(len(self.rules) - 1)

        for word in words:
            nchars = len(word)
            for j in range(nchars):
                if j == 0:
                    self.rules[0].append(word[j]+f"<{self.nRules}>")
                    self.nRules += 1
                elif j == nchars - 1:
                    self.rules.append([word[j]])
                    self.terminals.add(self.nRules - 1)
                else:
                    self.rules.append([word[j]+f"<{self.nRules}>"])
                    self.nRules += 1

        characters = set()
        for state in self.rules:
            for transitions in state:
                matched = re.match('^\w|^epsi', transitions)
                if matched:
                    characters.add(matched.group(0))
        self.alphabet = tuple(sorted(list(characters)))

class DeterministicFiniteAutomaton(FiniteAutomaton):
    def __init__(self, sourcefile:str):
        super.__init__(sourcefile)
    def Build(self):
        self.loadRead()
        self.__determinate()
        self.createStates()
    def __getindeterminations(self) -> list:
        inds = []

        for i in range(len(self.rules)):
            for char in self.alphabet:
                ind = Indetermination()
                temp = set()

                for j in range(len(self.rules[i])):
                    matched = re.match(f"{char}<(\d)>", self.rules[i][j])
                    if matched:
                        ind.parent = i
                        ind.simbol = char
                        temp.add(int(matched.group(1)))
                ind.states.extend(temp)
                if ind.isIndetermination():
                    inds.append(ind)
        return inds
    def __solveindeterminations(self, inds:list[Indetermination]) -> set[int]:
        reachbleRules = set()

        for ind in inds:
            self.rules.append(ind.Solve(self.rules, self.nRules, reachbleRules, self.terminals))
            reachbleRules.add(ind.parent)
            reachbleRules.add(self.nRules)

            self.nRules += 1
        
        return reachbleRules
    def __determinate(self):
        rstates = set()

        inds = self.__getindeterminations()

        while len(inds) > 0:
            rstates = rstates.union(self.__solveindeterminations(inds))
            inds = self.__getindeterminations()
        
        for i in range(self.nRules):
            if i in rstates:
                for production in self.rules[i]:
                    matched = re.match(f'\w<(\d)>', production)
                    if matched:
                        rstates.add(int(matched.group(1)))
        
        self.unreacheble = set([i for i in range(self.nRules)]).difference(rstates)