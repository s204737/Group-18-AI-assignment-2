"""
agm_tests.py
------------
Tests for the five AGM revision postulates.

Postulates tested:
  1. Success       phi ∈ B * phi
  2. Inclusion     B * phi ⊆ B + phi
  3. Vacuity       ¬phi ∉ B  =>  B * phi = B + phi
  4. Consistency   B * phi is consistent  (unless phi is a contradiction)
  5. Extensionality  phi ↔ psi tautology  =>  B * phi = B * psi
"""

from __future__ import annotations

from formula import Atom, Implies, Not, And, Or, Iff
from belief_base import BeliefBase
from entailment import entails, is_consistent
from operations import expand
from revision import revise


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _formulas_equal_as_sets(b1: BeliefBase, b2: BeliefBase) -> bool:
    f1 = b1.formulas()
    f2 = b2.formulas()
    for f in f1:
        if not entails(f2, f):
            return False
    for f in f2:
        if not entails(f1, f):
            return False
    return True


def _print_base(base: BeliefBase, label: str) -> None:
    print(f"\n    {label}:")
    for f, p in base:
        print(f"      [{p:2d}]  {f}")


def _print_result(postulate: str, passed: bool) -> None:
    status = "PASS" if passed else "FAIL"
    print(f"\n  >>> [{status}] {postulate} postulate\n")


# ---------------------------------------------------------------------------
# Postulate 1 — Success
# ---------------------------------------------------------------------------

def test_success() -> bool:
    print("\n" + "─" * 50)
    print("  POSTULATE 1: Success")
    print("  Claim: after revising with φ, φ must be in the result.")
    print("  Why:   revision is pointless if the new belief doesn't stick.")
    print("  Scene: doctor believed the patient has flu — flu test comes back negative.")

    flu   = Atom('flu')
    fever = Atom('fever')

    base = BeliefBase([
        (Implies(flu, fever), 8),
        (flu,                 5),
        (fever,               4),
    ])
    phi = Not(flu)

    print(f"\n  Revising with: {phi}")
    _print_base(base, "Belief base before revision")

    result = revise(base, phi, priority=7)
    _print_base(result, "Belief base after revision")

    passed = phi in result
    print(f"\n  Check: is {phi} in the revised base? {passed}")
    _print_result("Success", passed)
    return passed


# ---------------------------------------------------------------------------
# Postulate 2 — Inclusion
# ---------------------------------------------------------------------------

def test_inclusion() -> bool:
    print("\n" + "─" * 50)
    print("  POSTULATE 2: Inclusion")
    print("  Claim: B * φ ⊆ B + φ")
    print("  Why:   revision only removes beliefs (to fix conflicts).")
    print("         it should never introduce beliefs that weren't in")
    print("         the base or the new formula itself.")
    print("  Scene: patient was believed to have covid — doctor now confirms they are healthy.")

    covid   = Atom('covid')
    fatigue = Atom('fatigue')
    healthy = Atom('healthy')

    base = BeliefBase([
        (Implies(covid, fatigue), 8),
        (covid,                   6),
        (fatigue,                 5),
    ])
    phi = healthy

    print(f"\n  Revising with: {phi}")
    _print_base(base, "Belief base before revision")

    revised  = revise(base, phi, priority=7)
    expanded = expand(base, phi, priority=7)

    _print_base(revised,  "B * φ  (revised — conflicts removed first)")
    _print_base(expanded, "B + φ  (expanded — blind add, no conflict removal)")

    revised_set  = revised.to_set()
    expanded_set = expanded.to_set()
    extra = revised_set - expanded_set

    passed = revised_set.issubset(expanded_set)
    print(f"\n  Check: every belief in (B * φ) also appears in (B + φ)? {passed}")
    if extra:
        print(f"  Unexpected extra beliefs: {extra}")
    _print_result("Inclusion", passed)
    return passed


# ---------------------------------------------------------------------------
# Postulate 3 — Vacuity
# ---------------------------------------------------------------------------

def test_vacuity() -> bool:
    print("\n" + "─" * 50)
    print("  POSTULATE 3: Vacuity")
    print("  Claim: if B does not believe ¬φ, then B * φ = B + φ")
    print("  Why:   if there is no conflict, revision and expansion")
    print("         should be identical — no cleanup is needed.")

    fever = Atom('fever')
    cough = Atom('cough')
    covid = Atom('covid')

    base = BeliefBase([
        (fever, 6),
        (cough, 5),
    ])
    phi = covid

    precondition = not entails(base.formulas(), Not(phi))
    print(f"\n  Revising with: {phi}  (adding a covid belief to a base that has no opinion on covid)")
    print(f"  Pre-condition — base does NOT already believe ¬covid: {precondition}")
    _print_base(base, "Belief base before revision")

    revised  = revise(base, phi, priority=5)
    expanded = expand(base, phi, priority=5)

    _print_base(revised,  "B * φ  (revised)")
    _print_base(expanded, "B + φ  (expanded)")

    equal = _formulas_equal_as_sets(revised, expanded)
    passed = precondition and equal
    print(f"\n  Check: B * φ == B + φ? {equal}")
    _print_result("Vacuity", passed)
    return passed


# ---------------------------------------------------------------------------
# Postulate 4 — Consistency
# ---------------------------------------------------------------------------

def test_consistency() -> bool:
    print("\n" + "─" * 50)
    print("  POSTULATE 4: Consistency")
    print("  Claim: B * φ is consistent (unless φ itself is a contradiction).")
    print("  Why:   a belief base with a contradiction is useless —")
    print("         it entails everything, including false statements.")
    print("  Scene: patient was thought to have a cold — sore throat turns out to be absent.")

    cold        = Atom('cold')
    cough       = Atom('cough')
    sore_throat = Atom('sore_throat')

    base = BeliefBase([
        (Implies(cold, And(cough, sore_throat)), 9),
        (cold,                                   5),
        (sore_throat,                            4),
        (cough,                                  4),
    ])
    phi = Not(sore_throat)

    phi_is_contradiction = phi.is_contradiction()
    print(f"\n  Revising with: {phi}  (no sore throat after all)")
    print(f"  Note: {phi} is itself a contradiction? {phi_is_contradiction}")
    _print_base(base, "Belief base before revision")

    result = revise(base, phi, priority=6)
    _print_base(result, "Belief base after revision")

    consistent = is_consistent(result.formulas())
    passed = phi_is_contradiction or consistent
    print(f"\n  Check: is the revised base consistent? {consistent}")
    _print_result("Consistency", passed)
    return passed


# ---------------------------------------------------------------------------
# Postulate 5 — Extensionality
# ---------------------------------------------------------------------------

def test_extensionality() -> bool:
    print("\n" + "─" * 50)
    print("  POSTULATE 5: Extensionality")
    print("  Claim: if φ ↔ ψ is a tautology, then B * φ = B * ψ.")
    print("  Why:   logically equivalent formulas carry the same information.")
    print("         the engine must not treat them differently.")

    flu   = Atom('flu')
    fever = Atom('fever')

    base = BeliefBase([
        (flu,   5),
        (fever, 4),
    ])

    phi = Or(Not(flu), Not(fever))
    psi = Or(Not(fever), Not(flu))

    equivalence  = Iff(phi, psi)
    is_tautology = equivalence.is_tautology()

    print(f"\n  φ = {phi}")
    print(f"  ψ = {psi}")
    print(f"  φ ↔ ψ is a tautology (they mean the same thing): {is_tautology}")
    _print_base(base, "Belief base (same for both revisions)")

    result_phi = revise(base, phi, priority=6)
    result_psi = revise(base, psi, priority=6)

    _print_base(result_phi, "B * φ")
    _print_base(result_psi, "B * ψ")

    same   = _formulas_equal_as_sets(result_phi, result_psi)
    passed = is_tautology and same
    print(f"\n  Check: B * φ == B * ψ? {same}")
    _print_result("Extensionality", passed)
    return passed


# ---------------------------------------------------------------------------
# Run all tests
# ---------------------------------------------------------------------------

def run_all_tests() -> None:
    print("\n" + "=" * 50)
    print("  AGM Postulate Tests")
    print("  These verify the revision engine behaves rationally.")
    print("=" * 50)

    results = [
        test_success(),
        test_inclusion(),
        test_vacuity(),
        test_consistency(),
        test_extensionality(),
    ]

    passed = sum(results)
    total  = len(results)
    print("=" * 50)
    print(f"  {passed}/{total} postulates passed")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    run_all_tests()
