"""
entailment.py
-------------
Resolution-based logical entailment for propositional logic.

To check whether KB |= phi:
  1. Negate phi  -->  Not(phi)
  2. Convert KB ∪ {Not(phi)} to CNF
  3. Extract clauses
  4. Apply resolution until the empty clause is derived (=> entailed)
     or no new clauses can be added (=> not entailed)

No external logic libraries are used.
"""

from __future__ import annotations
from formula import Formula, Not, And
from typing import FrozenSet


Clause = FrozenSet[Formula]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def entails(kb: list[Formula], phi: Formula) -> bool:
    """
    Return True if kb logically entails phi (kb |= phi).
    Uses resolution refutation: tries to derive a contradiction from kb + {¬phi}.
    """
    formulas = list(kb) + [Not(phi)]
    clauses = _to_clause_set(formulas)
    return _resolution(clauses)


def is_consistent(formulas: list[Formula]) -> bool:
    """
    Return True if the set of formulas is satisfiable
    (i.e. does NOT entail a contradiction).
    """
    clauses = _to_clause_set(formulas)
    # If resolution on the formulas alone derives the empty clause => inconsistent
    return not _resolution(clauses)


def entails_negation(kb: list[Formula], phi: Formula) -> bool:
    """Convenience: check whether kb |= ¬phi."""
    return entails(kb, Not(phi))


# ---------------------------------------------------------------------------
# Resolution engine
# ---------------------------------------------------------------------------

def _to_clause_set(formulas: list[Formula]) -> set[Clause]:
    """Convert a list of formulas to a set of CNF clauses."""
    clauses: set[Clause] = set()
    for f in formulas:
        for clause in f.to_clauses():
            clauses.add(clause)
    return clauses


def _resolve(c1: Clause, c2: Clause) -> set[Clause]:
    """
    Apply the resolution rule to two clauses.
    For each literal L in c1 where ¬L is in c2, produce the resolvent:
      (c1 - {L}) ∪ (c2 - {¬L})
    Returns a set of resolvents (may be empty if no complementary literals).
    """
    resolvents = set()
    for literal in c1:
        complement = _negate_literal(literal)
        if complement in c2:
            resolvent = frozenset(
                (c1 - {literal}) | (c2 - {complement})
            )
            resolvents.add(resolvent)
    return resolvents


def _negate_literal(literal: Formula) -> Formula:
    """
    Return the negation of a literal.
    ¬(¬p) = p,  ¬p = ¬p
    """
    from formula import Atom, Not
    if isinstance(literal, Not) and isinstance(literal.operand, Formula):
        return literal.operand
    return Not(literal)


def _resolution(clauses: set[Clause]) -> bool:
    """
    Run the resolution algorithm.
    Returns True if the empty clause is derived (i.e. refutation found).
    Returns False if saturation is reached without finding the empty clause.
    """
    clauses = set(clauses)   # work on a copy

    while True:
        new_clauses: set[Clause] = set()
        clause_list = list(clauses)

        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                resolvents = _resolve(clause_list[i], clause_list[j])
                for r in resolvents:
                    if len(r) == 0:
                        return True          # empty clause => contradiction found
                    new_clauses.add(r)

        if new_clauses.issubset(clauses):
            return False                     # no new clauses => saturated, consistent

        clauses |= new_clauses


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from formula import Atom, Implies, Not, And, Or

    p, q, r = Atom('p'), Atom('q'), Atom('r')

    kb = [Implies(p, q), p]
    print(f"{{p→q, p}} |= q?       {entails(kb, q)}")       # True
    print(f"{{p→q, p}} |= r?       {entails(kb, r)}")       # False
    print(f"{{p→q, p}} |= ¬q?      {entails(kb, Not(q))}")  # False

    kb2 = [p, Not(p)]
    print(f"{{p, ¬p}} consistent?  {is_consistent(kb2)}")   # False

    kb3 = [p, q]
    print(f"{{p, q}} consistent?   {is_consistent(kb3)}")   # True
