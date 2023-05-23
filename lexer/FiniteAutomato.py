import re
from Indetermination import Indetermination

class FiniteAutomato:
    def __init__(self, sourcefile:str):
        self.sourcefile = sourcefile
        self.nStates = 0
        self.rules = []
        self.states = {}
        self.terminals = set()
        self.unreacheble = set()
        self.dead = set()
        self.alphabet = tuple()
    def Build(self):
        self.__loadRead()
        self.__determinate()
        self.__removeUnfinished()
        self.__removeDead()
    def __loadRead(self):
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
                new = "<"+str(self.nStates)+">"
                vars[j] = re.sub(state, new, vars[j])
            self.nStates+=1
        
        for var in vars:
            productions = var.split('::=')[1]
            self.rules.append(productions.split('|'))
            if re.search('epsi$|\w$|\w\|', productions):
                self.terminals.add(len(self.rules) - 1)

        for word in words:
            nchars = len(word)
            for j in range(nchars):
                if j == 0:
                    self.rules[0].append(word[j]+f"<{self.nStates}>")
                    self.nStates += 1
                elif j == nchars - 1:
                    self.rules.append([word[j]])
                    self.terminals.add(self.nStates - 1)
                else:
                    self.rules.append([word[j]+f"<{self.nStates}>"])
                    self.nStates += 1

        characters = set()
        for state in self.rules:
            for transitions in state:
                matched = re.match('^\w|^epsi', transitions)
                if matched:
                    characters.add(matched.group(0))
        self.alphabet = tuple(sorted(list(characters)))
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
            new_parent = list(filter(lambda x: False if re.match(f'{ind.simbol}<\d>',x) else True,self.rules[ind.parent]))
            new_parent.append(f'{ind.simbol}<{self.nStates}>')
            self.rules[ind.parent] = new_parent
 
            for production in new_parent:
                matched = re.match(f'\w<(\d)>', production)
                if matched:
                    reachbleRules.add(int(matched.group(1)))

            new_rule = []
            for s in ind.states:
                if s in self.terminals:
                    self.terminals.add(self.nStates)
                new_rule.extend(self.rules[s])
            self.rules.append(new_rule)

            for production in new_rule:
                matched = re.match(f'\w<(\d)>', production)
                if matched:
                    reachbleRules.add(int(matched.group(1)))

            reachbleRules.add(ind.parent)
            reachbleRules.add(self.nStates)

            self.nStates += 1
        
        return reachbleRules
    def __determinate(self):
        newRule = []
        rstates = set()

        inds = self.__getindeterminations()

        while len(inds) > 0:
            rstates = rstates.union(self.__solveindeterminations(inds))
            inds = self.__getindeterminations()
        
        print(rstates)
    def __removeDead(self):
        pass