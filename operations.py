"""
Implementation of AGM operations:Contraction and expansion of a belief base.

Expansion  B + phi:
  Simply add phi to the belief base at the given priority.

Contraction  B ÷ phi  (partial meet contraction):
  1. Find all maximal subsets of B that do NOT entail phi  (the "remainder sets")
  2. Use a selection function based on priority to pick the best remainder(s)
  3. Return their intersection

The selection function picks remainder(s) that retain the highest-priority
formulas — i.e. remainders that lose the least valuable beliefs.
"""

from __future__ import annotations
from itertools import combinations

from formula import Formula, Not
from belief_base import BeliefBase
from entailment import entails



# ---------------Expansion------------------------

def expand(base: BeliefBase, phi: Formula, priority: int = 5) -> BeliefBase:
    """
    B + phi: add phi to the belief base at the given priority.
    Returns a new BeliefBase (does not mutate the original).
    """
    result = base.copy()
    result.add(phi, priority)
    return result



# -----------------Contraction------------------------

def contract(base: BeliefBase, phi: Formula) -> BeliefBase:
    
    #B ÷ phi: remove phi from the belief base using partial meet contraction.

    #If the base does not entail phi, returns the base unchanged (vacuous contraction)
    #Returns a new BeliefBase (does not mutate the original)

    formulas = base.formulas()

    # Vacuity: if phi is not entailed, nothing to do
    if not entails(formulas, phi):
        return base.copy()

    # Find all remainder sets: maximal subsets that do NOT entail phi
    remainders = _remainder_sets(formulas, phi)

    if not remainders:
        # phi is a tautology — cannot be contracted, return empty base
        return BeliefBase()

    # Select the best remainders using the priority-based selection function
    selected = _selection_function(remainders, base)

    # The contracted base is the intersection of selected remainders
    if not selected:
        return BeliefBase()

    intersected_formulas = set(selected[0])
    for remainder in selected[1:]:
        intersected_formulas &= set(remainder)

    # Rebuild belief base preserving original priorities
    result = BeliefBase()
    for f in intersected_formulas:
        p = base.priority_of(f)
        if p is not None:
            result.add(f, p)

    return result


# ---------------------Remainder sets-----------------------

def _remainder_sets(formulas: list[Formula], phi: Formula) -> list[list[Formula]]:
    """
    Compute B ⊥ phi: all maximal subsets of `formulas` that do not entail phi.

    Algorithm:
      For each subset (from largest to smallest), check if it doesn't entail phi.
      Keep only the maximal ones (no subset of a found remainder is kept if
      a larger non-entailing subset exists).
    """
    n = len(formulas)
    remainders = []

    # Try subsets from largest to smallest
    for size in range(n, -1, -1):
        for subset in combinations(formulas, size):
            subset = list(subset)
            if not entails(subset, phi):
                # Check it's not a subset of an already-found remainder
                if not _is_subset_of_any(subset, remainders):
                    remainders.append(subset)

    return remainders


def _is_subset_of_any(candidate: list[Formula], remainders: list[list[Formula]]) -> bool:
    #Return True if candidate is a strict subset of any remainder already found.
    candidate_set = set(candidate)
    for r in remainders:
        if candidate_set < set(r):   # strict subset
            return True
    return False


# ----------------Selection function--------------------------

def _selection_function(
    remainders: list[list[Formula]],
    base: BeliefBase
) -> list[list[Formula]]:
    """
    Priority-based selection: pick the remainder(s) with the highest total
    priority score. This implements an epistemic entrenchment ordering —
    we prefer to keep high-priority beliefs.

    Returns a list of selected remainders (usually just one, but ties are
    broken by keeping all tied remainders and intersecting them).
    """
    def score(remainder: list[Formula]) -> int:
        return sum(base.priority_of(f) or 0 for f in remainder)

    if not remainders:
        return []

    best_score = max(score(r) for r in remainders)
    return [r for r in remainders if score(r) == best_score]


# ------------Test Demo----------------------

if __name__ == "__main__":
    from formula import Atom, Implies, Not

    p, q, r = Atom('p'), Atom('q'), Atom('r')

    base = BeliefBase([
        (Implies(p, q), 8),   # p → q  (high priority)
        (p,             5),   # p      (medium)
        (q,             3),   # q      (low)
    ])

    print("Initial base:")
    print(base)

    # Contract q  — should remove q (lowest priority) since p→q,p also entails q
    contracted = contract(base, q)
    print("\nAfter contracting q:")
    print(contracted)

    # Expand with ¬p
    expanded = expand(base, Not(p), priority=7)
    print("\nAfter expanding with ¬p:")
    print(expanded)
