import re

class FiniteAutomato:
    def __init__(self, sourcefile:str):
        self.sourcefile = sourcefile
        self.nStates = 0
        self.rules = []
    def LoadRead(self):
        file = open(self.sourcefile)

        vars = []
        tokens = []

        for line in file.readlines():
            if re.search("^<\w>(.*)::=(.*)", line):
                vars.append(line.replace('\n', '').replace(' ', ''))
            else:
                tokens.append(line.replace('\n', '').replace(' ', ''))

        file.close()

        for i in range(len(vars)):
            state = vars[i].split('::=')[0]

            for j in range(len(vars)):
                new = "<"+str(self.nStates)+">"
                vars[j] = re.sub(state, new, vars[j])
            
            self.nStates+=1
        
        print(vars, tokens)
    def Determinate(self):
        pass
    def RemoveUnfinished(self):
        pass
    def RemoveDead(self):
        pass