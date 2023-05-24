from FiniteAutomaton import DeterministicFiniteAutomaton

automaton = DeterministicFiniteAutomaton("./input/rules.in")
automaton.Build()
print(automaton.states)
print(automaton.nextState(automaton.initialState, 's'))