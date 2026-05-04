"""
Belief base: a prioritised set of propositional formulas.

Each belief is stored as (formula, priority) where priority is an integer.
Higher priority = more entrenched = harder to remove during contraction.
"""

from __future__ import annotations
from formula import Formula, Not


class BeliefBase:
    
    #A finite, prioritised belief base ->

    #Internally stored as a list of (Formula, int) pairs.
    #Duplicate formulas are not allowed; adding an existing formula
    #updates its priority instead

    def __init__(self, beliefs: list[tuple[Formula, int]] | None = None):
        # Store as list of (formula, priority)
        self._beliefs: list[tuple[Formula, int]] = []
        for formula, priority in (beliefs or []):
            self.add(formula, priority)


    # -----------Main Features------------

    def add(self, formula: Formula, priority: int) -> None:
        #Add a formula with the given priority. Updates priority if already present
        for i, (f, _) in enumerate(self._beliefs):
            if f == formula:
                self._beliefs[i] = (formula, priority)
                return
        self._beliefs.append((formula, priority))

    def remove(self, formula: Formula) -> None:
        #Remove a formula (no-op if not present)
        self._beliefs = [(f, p) for f, p in self._beliefs if f != formula]

    def __contains__(self, formula: Formula) -> bool:
        return any(f == formula for f, _ in self._beliefs)

    def __iter__(self):
        #Iterate over (formula, priority) pairs, highest priority first
        return iter(sorted(self._beliefs, key=lambda x: -x[1]))

    def __len__(self) -> int:
        return len(self._beliefs)

    def __repr__(self) -> str:
        lines = [f"  [{p:2d}] {f}" for f, p in self]
        return "BeliefBase(\n" + "\n".join(lines) + "\n)"

    def formulas(self) -> list[Formula]:
        #Return all formulas, sorted by descending priority
        return [f for f, _ in self]

    def priority_of(self, formula: Formula) -> int | None:
        for f, p in self._beliefs:
            if f == formula:
                return p
        return None

    def copy(self) -> "BeliefBase":
        return BeliefBase(list(self._beliefs))

    def is_empty(self) -> bool:
        return len(self._beliefs) == 0

    def to_set(self) -> set[Formula]:
        return set(self.formulas())

    
    # --------------Consistency---------------------

    def is_consistent(self) -> bool:
        
        #Return True if the belief base is satisfiable -->
        #i.e. there exists at least one truth assignment satisfying all beliefs
        from entailment import is_consistent
        return is_consistent(self.formulas())
