"""

Propositional logic model for CNF conversion
for the belief revision engine. This acts as the "data model layer". 
It represents & evaluates formulas, converts them to CNF and feeds them into 
the resolution based entailment. 

Supported connectives:
  Atom(name)          -- atomic proposition, e.g. Atom('p')
  Not(f)              -- negation:     ¬f
  And(f, g)           -- conjunction:  f ∧ g
  Or(f, g)            -- disjunction:  f ∨ g
  Implies(f, g)       -- implication:  f → g
  Iff(f, g)           -- biconditional: f ↔ g
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import FrozenSet, Set



# ---------------Base class------------------------


class Formula:
    #Abstract base for all propositional formulas

    def __neg__(self) -> "Not":
        return Not(self)

    def __and__(self, other: "Formula") -> "And":
        return And(self, other)

    def __or__(self, other: "Formula") -> "Or":
        return Or(self, other)

    def __rshift__(self, other: "Formula") -> "Implies":
        #Use >> as implication: p >> q  means  p → q
        return Implies(self, other)

    def atoms(self) -> Set[str]:
        #Return the set of all atom names in this formula
        raise NotImplementedError

    def evaluate(self, assignment: dict[str, bool]) -> bool:
        #Evaluate the formula under a truth assignment
        raise NotImplementedError

    def to_cnf(self) -> "Formula":
        #Return an equivalent formula in Conjunctive Normal Form
        f = self._eliminate_iff()
        f = f._eliminate_implies()
        f = f._push_negation_inward()
        f = f._distribute_or_over_and()
        return f

    # -- CNF pipeline steps (internal) --------------------------------------

    def _eliminate_iff(self) -> "Formula":
        raise NotImplementedError

    def _eliminate_implies(self) -> "Formula":
        raise NotImplementedError

    def _push_negation_inward(self) -> "Formula":
        raise NotImplementedError

    def _distribute_or_over_and(self) -> "Formula":
        raise NotImplementedError

    def is_literal(self) -> bool:
        #True if this is an Atom or a Not(Atom)
        return False

    def is_tautology(self) -> bool:
        #Check whether the formula is a tautology (true in all worlds)
        for assignment in _all_assignments(self.atoms()):
            if not self.evaluate(assignment):
                return False
        return True

    def is_contradiction(self) -> bool:
        #Check whether the formula is unsatisfiable
        for assignment in _all_assignments(self.atoms()):
            if self.evaluate(assignment):
                return False
        return True

    def to_clauses(self) -> list[FrozenSet["Formula"]]:
        #Convert to CNF and return a list of clauses
        #Each clause is a frozenset of literals (Atom or Not(Atom))
        cnf = self.to_cnf()
        return _extract_clauses(cnf)

    def __repr__(self) -> str:
        raise NotImplementedError

    def __eq__(self, other: object) -> bool:
        raise NotImplementedError

    def __hash__(self) -> int:
        raise NotImplementedError


# ---------------Concrete formula types-------------------------

@dataclass(frozen=True)
class Atom(Formula):
    name: str

    def atoms(self):
        return {self.name}

    def evaluate(self, assignment):
        if self.name not in assignment:
            raise ValueError(f"Atom '{self.name}' not in assignment")
        return assignment[self.name]

    def is_literal(self):
        return True

    def _eliminate_iff(self):      return self
    def _eliminate_implies(self):  return self
    def _push_negation_inward(self): return self
    def _distribute_or_over_and(self): return self

    def __repr__(self):
        return self.name


@dataclass(frozen=True)
class Not(Formula):
    operand: Formula

    def atoms(self):
        return self.operand.atoms()

    def evaluate(self, assignment):
        return not self.operand.evaluate(assignment)

    def is_literal(self):
        return isinstance(self.operand, Atom)

    def _eliminate_iff(self):
        return Not(self.operand._eliminate_iff())

    def _eliminate_implies(self):
        return Not(self.operand._eliminate_implies())

    def _push_negation_inward(self):
        o = self.operand
        # ¬¬A  →  A
        if isinstance(o, Not):
            return o.operand._push_negation_inward()
        # ¬(A ∧ B)  →  ¬A ∨ ¬B   (De Morgan)
        if isinstance(o, And):
            return Or(Not(o.left), Not(o.right))._push_negation_inward()
        # ¬(A ∨ B)  →  ¬A ∧ ¬B   (De Morgan)
        if isinstance(o, Or):
            return And(Not(o.left), Not(o.right))._push_negation_inward()
        # ¬Atom stays as-is (already a literal)
        return self

    def _distribute_or_over_and(self):
        return Not(self.operand._distribute_or_over_and())

    def __repr__(self):
        return f"¬{self.operand!r}"


@dataclass(frozen=True)
class And(Formula):
    left: Formula
    right: Formula

    def atoms(self):
        return self.left.atoms() | self.right.atoms()

    def evaluate(self, assignment):
        return self.left.evaluate(assignment) and self.right.evaluate(assignment)

    def _eliminate_iff(self):
        return And(self.left._eliminate_iff(), self.right._eliminate_iff())

    def _eliminate_implies(self):
        return And(self.left._eliminate_implies(), self.right._eliminate_implies())

    def _push_negation_inward(self):
        return And(self.left._push_negation_inward(),
                   self.right._push_negation_inward())

    def _distribute_or_over_and(self):
        return And(self.left._distribute_or_over_and(),
                   self.right._distribute_or_over_and())

    def __repr__(self):
        return f"({self.left!r} ∧ {self.right!r})"


@dataclass(frozen=True)
class Or(Formula):
    left: Formula
    right: Formula

    def atoms(self):
        return self.left.atoms() | self.right.atoms()

    def evaluate(self, assignment):
        return self.left.evaluate(assignment) or self.right.evaluate(assignment)

    def _eliminate_iff(self):
        return Or(self.left._eliminate_iff(), self.right._eliminate_iff())

    def _eliminate_implies(self):
        return Or(self.left._eliminate_implies(), self.right._eliminate_implies())

    def _push_negation_inward(self):
        return Or(self.left._push_negation_inward(),
                  self.right._push_negation_inward())

    def _distribute_or_over_and(self):
        #Key step: (A ∨ (B ∧ C))  →  (A ∨ B) ∧ (A ∨ C)
        l = self.left._distribute_or_over_and()
        r = self.right._distribute_or_over_and()

        if isinstance(r, And):
            return And(Or(l, r.left)._distribute_or_over_and(),
                       Or(l, r.right)._distribute_or_over_and())
        if isinstance(l, And):
            return And(Or(l.left, r)._distribute_or_over_and(),
                       Or(l.right, r)._distribute_or_over_and())
        return Or(l, r)

    def __repr__(self):
        return f"({self.left!r} ∨ {self.right!r})"


@dataclass(frozen=True)
class Implies(Formula):
    antecedent: Formula
    consequent: Formula

    def atoms(self):
        return self.antecedent.atoms() | self.consequent.atoms()

    def evaluate(self, assignment):
        return (not self.antecedent.evaluate(assignment)
                or self.consequent.evaluate(assignment))

    def _eliminate_iff(self):
        return Implies(self.antecedent._eliminate_iff(),
                       self.consequent._eliminate_iff())

    def _eliminate_implies(self):
        # A → B  becomes  ¬A ∨ B
        return Or(Not(self.antecedent), self.consequent)._eliminate_implies()

    def _push_negation_inward(self):
        # Should be called after _eliminate_implies, so this shouldn't appear
        return self._eliminate_implies()._push_negation_inward()

    def _distribute_or_over_and(self):
        return self._eliminate_implies()._distribute_or_over_and()

    def __repr__(self):
        return f"({self.antecedent!r} → {self.consequent!r})"


@dataclass(frozen=True)
class Iff(Formula):
    left: Formula
    right: Formula

    def atoms(self):
        return self.left.atoms() | self.right.atoms()

    def evaluate(self, assignment):
        return self.left.evaluate(assignment) == self.right.evaluate(assignment)

    def _eliminate_iff(self):
        # A ↔ B  becomes  (A → B) ∧ (B → A)
        l = self.left._eliminate_iff()
        r = self.right._eliminate_iff()
        return And(Implies(l, r), Implies(r, l))

    def _eliminate_implies(self):
        return self._eliminate_iff()._eliminate_implies()

    def _push_negation_inward(self):
        return self._eliminate_iff()._push_negation_inward()

    def _distribute_or_over_and(self):
        return self._eliminate_iff()._distribute_or_over_and()

    def __repr__(self):
        return f"({self.left!r} ↔ {self.right!r})"


# -----------Helper Functions for CNF conversion and clause extraction----------------------


def _all_assignments(atom_names: Set[str]):
    #Generate all truth assignments over the given atoms
    names = sorted(atom_names)
    n = len(names)
    for i in range(2 ** n):
        yield {names[j]: bool((i >> j) & 1) for j in range(n)}


def _extract_clauses(cnf: Formula) -> list[FrozenSet[Formula]]:
    #Walk a CNF formula and collect each clause as a frozenset of literals
    #A CNF formula is an And of Ors of literals
    clauses = []
    _collect_and(cnf, clauses)
    return clauses


def _collect_and(f: Formula, clauses: list):
    if isinstance(f, And):
        _collect_and(f.left, clauses)
        _collect_and(f.right, clauses)
    else:
        clause = frozenset(_collect_or(f))
        clauses.append(clause)


def _collect_or(f: Formula) -> list[Formula]:
    if isinstance(f, Or):
        return _collect_or(f.left) + _collect_or(f.right)
    return [f]


# --------------Quick demo--------------------

if __name__ == "__main__":
    p, q, r = Atom('p'), Atom('q'), Atom('r')

    # Build:  (p → ¬q) ∧ (q ∨ r)
    formula = (p >> -q) & (q | r)
    print("Formula:    ", formula)
    print("CNF:        ", formula.to_cnf())
    print("Clauses:    ", formula.to_clauses())
    print()

    # Tautology check: p ∨ ¬p
    taut = p | -p
    print(f"{taut} is tautology: {taut.is_tautology()}")

    # Biconditional
    bic = Iff(p, q)
    print("p ↔ q CNF:  ", bic.to_cnf())
    print("Clauses:    ", bic.to_clauses())
