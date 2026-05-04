"""

Implementation of Belief revision via the Levi Identity:

    B * phi  =  (B ÷ ¬phi) + phi

Steps:
  1. Contract the belief base by ¬phi  (remove anything inconsistent with phi)
  2. Expand the result with phi        (add the new information)

This guarantees the AGM postulates are satisfied when contraction
satisfies the contraction postulates.
"""

from __future__ import annotations

from formula import Formula, Not
from belief_base import BeliefBase
from operations import contract, expand


def revise(base: BeliefBase, phi: Formula, priority: int = 5) -> BeliefBase:
    """
    B * phi: revise the belief base with phi using the Levi Identity.

    Parameters
    ----------
    base     : the current belief base
    phi      : the new formula to incorporate
    priority : the priority assigned to phi in the resulting base

    Returns a new BeliefBase (does not mutate the original).
    """
    # Step 1: contract by ¬phi
    contracted = contract(base, Not(phi))

    # Step 2: expand with phi
    revised = expand(contracted, phi, priority=priority)

    return revised



# -----------------Quick demo--------------------------------------

if __name__ == "__main__":
    from formula import Atom, Implies, Not, And

    p, q, r = Atom('p'), Atom('q'), Atom('r')

    base = BeliefBase([
        (Implies(p, q), 8),
        (p,             5),
        (q,             3),
    ])

    print("Initial base:")
    print(base)

    # Revise with ¬q — forces removal of things that imply q
    revised = revise(base, Not(q), priority=7)
    print("\nAfter revising with ¬q:")
    print(revised)

    # Revise with r — no conflict, should just add r
    revised2 = revise(base, r, priority=4)
    print("\nAfter revising with r (no conflict):")
    print(revised2)
