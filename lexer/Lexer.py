from FiniteAutomato import FiniteAutomato

af = FiniteAutomato("./input/rules.in")
af.LoadRead()
af.Determinate()
af.RemoveUnfinished()
af.RemoveDead()