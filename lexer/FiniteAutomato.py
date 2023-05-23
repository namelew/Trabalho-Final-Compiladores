import re

class FiniteAutomato:
    def __init__(self, sourcefile:str):
        self.sourcefile = sourcefile
        self.nStates = 0
        self.rules = []
        self.terminals = set()
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
            if re.search('^epsi$|^\w$', productions):
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
    def __determinate(self):
        pass
    def __removeUnfinished(self):
        pass
    def __removeDead(self):
        pass