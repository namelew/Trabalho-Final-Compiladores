import re
class Indetermination:
    def __init__(self) -> None:
        self.parent:int = 0
        self.simbol:str = ''
        self.states = []
        self.solution = ''
    def isIndetermination(self) -> bool:
        return len(self.states) > 1
    def Solve(self, rules:list[list[str]], newRules:list[list[str]],nrules:int, reachble:set[int], terminals:set[int], keywords:set[int]) -> list[str]:
        # criando modificando regra onde ocorreu a interminização
        new_parent = list(filter(lambda x: False if re.match(f'^{self.simbol}<\d+>$',x) else True, rules[self.parent]))
        new_parent.append(f'{self.simbol}<{nrules}>')
        self.solution = f'{self.simbol}<{nrules}>'
        # criando nova regra
        new_rule = []
        unionParents = set()
        for s in self.states:
            if s in terminals:
                terminals.add(nrules)
                if s in keywords:
                    keywords.add(nrules)
            for production in rules[s]:
                unionParents.add(production)
        # agora não é só fazer ele não resolver de novo inderminizações já resolvidas
        new_rule.extend(unionParents)

        newRules[self.parent] = new_parent
        # atualizando lista de terminais
        productions = list()
        productions.extend(new_rule)
        for production in productions:
            matched = re.match(f'^\w<(\d+)>$', production)
            if matched:
                reachble.add(int(matched.group(1)))
        return new_rule
    def __str__(self) -> str:
        return f"{self.parent} {self.simbol} {self.states}"