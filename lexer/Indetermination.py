import re
class Indetermination:
    def __init__(self) -> None:
        self.parent = 0
        self.simbol = ''
        self.states = []
    def isIndetermination(self) -> bool:
        return len(self.states) > 1
    def Solve(self, rules:list[list[str]], nrules:int, reachble:set[int], terminals:set[int]) -> list[str]:
        new_parent = list(filter(lambda x: False if re.match(f'{self.simbol}<\d>',x) else True, rules[self.parent]))
        new_parent.append(f'{self.simbol}<{nrules}>')
        rules[self.parent] = new_parent

        new_rule = []
        for s in self.states:
            if s in terminals:
                terminals.add(nrules)
            new_rule.extend(rules[s])
        
        for production in new_parent:
            matched = re.match(f'\w<(\d)>', production)
            if matched:
                reachble.add(int(matched.group(1)))
        
        for production in new_rule:
            matched = re.match(f'\w<(\d)>', production)
            if matched:
                reachble.add(int(matched.group(1)))
        
        return new_rule
    def __str__(self) -> str:
        return f"{self.parent} {self.simbol} {self.states}"