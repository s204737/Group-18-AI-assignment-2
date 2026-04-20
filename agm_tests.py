"""
agm_tests.py
------------
Tests for the five AGM revision postulates.

  1. Success          phi ∈ B * phi
  2. Inclusion        B * phi ⊆ B + phi
  3. Vacuity          ¬phi ∉ B  =>  B * phi = B + phi
  4. Consistency      B * phi is consistent  (unless phi is a contradiction)
  5. Extensionality   phi ↔ psi tautology  =>  B * phi = B * psi
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
    print(f"\n  [{status}] {postulate}\n")


# ---------------------------------------------------------------------------
# Postulate 1 — Success
# ---------------------------------------------------------------------------

def test_success() -> bool:
    print("\n" + "─" * 50)
    print("  Success  —  phi must be in B * phi")
    print("  Storm forecast revised with ¬storm (no wind observed)")

    storm = Atom('storm')
    wind  = Atom('wind')

    base = BeliefBase([
        (Implies(storm, wind), 8),
        (storm,                5),
        (wind,                 4),
    ])
    phi = Not(storm)

    _print_base(base, "Before")
    result = revise(base, phi, priority=7)
    _print_base(result, "After revising with ¬storm")

    passed = phi in result
    print(f"\n  ¬storm in revised base: {passed}")
    _print_result("Success", passed)
    return passed


# ---------------------------------------------------------------------------
# Postulate 2 — Inclusion
# ---------------------------------------------------------------------------

def test_inclusion() -> bool:
    print("\n" + "─" * 50)
    print("  Inclusion  —  B * phi ⊆ B + phi")
    print("  Storm expected — satellite confirms clear skies")

    storm = Atom('storm')
    rain  = Atom('rain')
    clear = Atom('clear')

    base = BeliefBase([
        (Implies(storm, rain), 8),
        (storm,                6),
        (rain,                 5),
    ])
    phi = clear

    revised  = revise(base, phi, priority=7)
    expanded = expand(base, phi, priority=7)

    _print_base(revised,  "B * phi  (revised)")
    _print_base(expanded, "B + phi  (expanded)")

    revised_set  = revised.to_set()
    expanded_set = expanded.to_set()
    extra  = revised_set - expanded_set
    passed = revised_set.issubset(expanded_set)

    print(f"\n  B * phi ⊆ B + phi: {passed}")
    if extra:
        print(f"  Unexpected extra beliefs: {extra}")
    _print_result("Inclusion", passed)
    return passed


# ---------------------------------------------------------------------------
# Postulate 3 — Vacuity
# ---------------------------------------------------------------------------

def test_vacuity() -> bool:
    print("\n" + "─" * 50)
    print("  Vacuity  —  if ¬phi ∉ B then B * phi = B + phi")
    print("  Base {rain, wind} has no opinion on frost — revision equals expansion")

    rain  = Atom('rain')
    wind  = Atom('wind')
    frost = Atom('frost')

    base = BeliefBase([
        (rain, 6),
        (wind, 5),
    ])
    phi = frost

    precondition = not entails(base.formulas(), Not(phi))
    _print_base(base, "Before")

    revised  = revise(base, phi, priority=5)
    expanded = expand(base, phi, priority=5)

    _print_base(revised,  "B * phi")
    _print_base(expanded, "B + phi")

    equal  = _formulas_equal_as_sets(revised, expanded)
    passed = precondition and equal
    print(f"\n  ¬frost not in base: {precondition}  |  B * phi == B + phi: {equal}")
    _print_result("Vacuity", passed)
    return passed


# ---------------------------------------------------------------------------
# Postulate 4 — Consistency
# ---------------------------------------------------------------------------

def test_consistency() -> bool:
    print("\n" + "─" * 50)
    print("  Consistency  —  B * phi must be satisfiable")
    print("  Frost forecast (requires cold ∧ ¬rain) revised with rain")

    frost = Atom('frost')
    cold  = Atom('cold')
    rain  = Atom('rain')

    base = BeliefBase([
        (Implies(frost, And(cold, Not(rain))), 9),
        (frost,                                5),
        (cold,                                 4),
    ])
    phi = rain

    _print_base(base, "Before")
    result = revise(base, phi, priority=6)
    _print_base(result, "After revising with rain")

    consistent = is_consistent(result.formulas())
    passed = phi.is_contradiction() or consistent
    print(f"\n  Revised base is consistent: {consistent}")
    _print_result("Consistency", passed)
    return passed


# ---------------------------------------------------------------------------
# Postulate 5 — Extensionality
# ---------------------------------------------------------------------------

def test_extensionality() -> bool:
    print("\n" + "─" * 50)
    print("  Extensionality  —  if phi ↔ psi is a tautology then B * phi = B * psi")
    print("  (¬storm ∨ ¬rain)  and  (¬rain ∨ ¬storm)  are logically equivalent")

    storm = Atom('storm')
    rain  = Atom('rain')

    base = BeliefBase([
        (storm, 5),
        (rain,  4),
    ])

    phi = Or(Not(storm), Not(rain))
    psi = Or(Not(rain),  Not(storm))

    is_tautology = Iff(phi, psi).is_tautology()

    result_phi = revise(base, phi, priority=6)
    result_psi = revise(base, psi, priority=6)

    _print_base(result_phi, "B * phi")
    _print_base(result_psi, "B * psi")

    same   = _formulas_equal_as_sets(result_phi, result_psi)
    passed = is_tautology and same
    print(f"\n  phi ↔ psi tautology: {is_tautology}  |  B * phi == B * psi: {same}")
    _print_result("Extensionality", passed)
    return passed


# ---------------------------------------------------------------------------
# Run all tests
# ---------------------------------------------------------------------------

def run_all_tests() -> None:
    print("\n" + "=" * 50)
    print("  AGM Postulate Tests")
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
    print(f"  {passed}/{total} passed")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    run_all_tests()
