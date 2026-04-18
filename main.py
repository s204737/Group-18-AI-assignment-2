"""
main.py
-------
Entry point for the belief revision engine.
Runs the medical diagnosis demo and then the AGM postulate tests.
"""

from formula import Atom, Implies, Not, And, Or
from belief_base import BeliefBase
from operations import expand, contract
from revision import revise
from agm_tests import run_all_tests
from domain import (
    INITIAL_BELIEFS, SCENARIOS,
    fever, cough, fatigue, sore_throat,
    flu, covid, cold, healthy,
    print_belief_base,
)


def run_demo():
    print("\n" + "=" * 60)
    print("  Belief Revision Engine — Medical Diagnosis Demo")
    print("=" * 60)

    # Build initial belief base from domain
    base = BeliefBase(INITIAL_BELIEFS)
    print_belief_base(list(base), "Initial belief base")

    # Run each revision scenario
    for i, (description, phi, *_) in enumerate(SCENARIOS, 1):
        print(f"Scenario {i}: {description}")
        print(f"  Revising with: {phi}")
        base = revise(base, phi, priority=7)
        print_belief_base(list(base), f"Belief base after scenario {i}")


def run_single_revision():
    """
    Focused example: start with flu diagnosis, receive negative flu test.
    Shows the core revision logic clearly.
    """
    print("\n" + "=" * 60)
    print("  Core example: flu test comes back negative")
    print("=" * 60)

    base = BeliefBase([
        (Implies(flu, And(fever, cough)),   10),
        (Implies(covid, And(fever, fatigue)), 10),
        (Implies(healthy, Not(fever)),       10),
        (Implies(flu, Not(covid)),            9),
        (fever,   6),
        (cough,   6),
        (fatigue, 5),
        (flu,     3),   # working hypothesis — low priority, first to go
    ])

    print_belief_base(list(base), "Before revision")

    revised = revise(base, Not(flu), priority=8)

    print_belief_base(list(revised), "After revising with ¬flu")
    print("  Note: 'flu' was dropped (low priority).")
    print("  Background knowledge (flu→fever∧cough) is preserved.")


if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    if "--doctor" in args or "-d" in args:
        from doctor import run_doctor_mode
        run_doctor_mode()
    elif "--interactive" in args or "-i" in args:
        from cli import run_cli
        run_cli()
    elif "--single" in args:
        run_single_revision()
    elif "--demo" in args:
        run_demo()
    elif "--tests" in args:
        run_all_tests()
    else:
        run_single_revision()
        run_demo()
        run_all_tests()
