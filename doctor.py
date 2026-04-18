"""
doctor.py
---------
Guided diagnostic interface for the belief revision engine.

The user plays the role of a doctor entering patient observations.
After each input the belief base is revised and the current diagnosis
is printed.
"""

from formula import Atom, Not, Implies, And
from belief_base import BeliefBase
from revision import revise
from entailment import entails

# ---------------------------------------------------------------------------
# Atoms
# ---------------------------------------------------------------------------

fever       = Atom('fever')
cough       = Atom('cough')
fatigue     = Atom('fatigue')
sore_throat = Atom('sore_throat')
flu         = Atom('flu')
covid       = Atom('covid')
cold        = Atom('cold')
healthy     = Atom('healthy')

# ---------------------------------------------------------------------------
# Background knowledge (never revised away)
# ---------------------------------------------------------------------------

BACKGROUND = [
    (Implies(flu,     And(fever, cough)),        10),
    (Implies(covid,   And(fever, fatigue)),       10),
    (Implies(cold,    And(cough, sore_throat)),   10),
    (Implies(healthy, Not(fever)),               10),
    (Implies(healthy, Not(cough)),               10),
    (Implies(flu,     Not(covid)),                9),
    (Implies(flu,     Not(cold)),                 9),
    (Implies(flu,     Not(healthy)),              9),
    (Implies(covid,   Not(flu)),                  9),
    (Implies(covid,   Not(cold)),                 9),
    (Implies(covid,   Not(healthy)),              9),
    (Implies(cold,    Not(flu)),                  9),
    (Implies(cold,    Not(covid)),                9),
    (Implies(cold,    Not(healthy)),              9),
    (Implies(healthy, Not(flu)),                  9),
    (Implies(healthy, Not(covid)),                9),
    (Implies(healthy, Not(cold)),                 9),
]

CONDITIONS  = [flu, covid, cold, healthy]
COND_NAMES  = {flu: "Flu", covid: "COVID-19", cold: "Common Cold", healthy: "Healthy"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ask(prompt: str) -> bool | None:
    """Ask a yes/no/unknown question. Returns True/False/None."""
    while True:
        ans = input(f"  {prompt} [yes / no / unknown]: ").strip().lower()
        if ans in ('yes', 'y'):
            return True
        if ans in ('no', 'n'):
            return False
        if ans in ('unknown', 'u', ''):
            return None
        print("  Please answer yes, no, or unknown.")


def _print_diagnosis(base: BeliefBase) -> None:
    formulas = base.formulas()
    print("\n  --- Current diagnosis ---")
    found_any = False
    for cond in CONDITIONS:
        if entails(formulas, cond):
            print(f"  >> {COND_NAMES[cond]} is supported")
            found_any = True
    if not found_any:
        print("  >> No definitive diagnosis yet")
    print()


def _separator() -> None:
    print("\n" + "-" * 50)


# ---------------------------------------------------------------------------
# Main flow
# ---------------------------------------------------------------------------

def run_doctor_mode() -> None:
    print("\n" + "=" * 56)
    print("  Medical Belief Revision — Doctor Interface")
    print("=" * 56)
    print("  Answer questions about the patient.")
    print("  Type 'unknown' (or press Enter) to skip a question.\n")

    base = BeliefBase(BACKGROUND)

    # --- Symptom observations ---
    _separator()
    print("  STEP 1: Observed symptoms\n")

    symptom_questions = [
        (fever,       "Does the patient have a fever?"),
        (cough,       "Does the patient have a cough?"),
        (fatigue,     "Does the patient report fatigue?"),
        (sore_throat, "Does the patient have a sore throat?"),
    ]

    for atom, question in symptom_questions:
        ans = _ask(question)
        if ans is True:
            base = revise(base, atom,      priority=7)
        elif ans is False:
            base = revise(base, Not(atom), priority=7)
        # None = skip

    _print_diagnosis(base)

    # --- Lab / test results ---
    _separator()
    print("  STEP 2: Test results (if available)\n")

    test_questions = [
        (flu,     "Flu test result:    positive?"),
        (covid,   "COVID test result:  positive?"),
    ]

    for atom, question in test_questions:
        ans = _ask(question)
        if ans is True:
            base = revise(base, atom,      priority=9)
        elif ans is False:
            base = revise(base, Not(atom), priority=9)

    _print_diagnosis(base)

    # --- Doctor's clinical judgement ---
    _separator()
    print("  STEP 3: Clinical judgement (optional)\n")

    clinical_questions = [
        (healthy, "Does the patient appear healthy overall?"),
        (cold,    "Does the presentation suggest a common cold?"),
    ]

    for atom, question in clinical_questions:
        ans = _ask(question)
        if ans is True:
            base = revise(base, atom,      priority=6)
        elif ans is False:
            base = revise(base, Not(atom), priority=6)

    # --- Final diagnosis ---
    _separator()
    print("\n  FINAL DIAGNOSIS\n")
    formulas = base.formulas()
    concluded = [c for c in CONDITIONS if entails(formulas, c)]

    if concluded:
        for c in concluded:
            print(f"  ** {COND_NAMES[c]} **")
    else:
        print("  Inconclusive — insufficient information for a definitive diagnosis.")

    print("\n  Final belief base:")
    for formula, priority in sorted(base, key=lambda x: -x[1]):
        print(f"    [{priority:2d}]  {formula}")
    print()


if __name__ == "__main__":
    run_doctor_mode()
