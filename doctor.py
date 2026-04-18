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
    print("""
  How this works:
    You are the doctor. Answer each question about your patient.
    The engine updates its beliefs after every answer and narrows
    down the diagnosis automatically.

    For each question, type:
      yes     — you observed this / the test was positive
      no      — you confirmed this is absent / test was negative
      unknown — you don't know yet, skip this question

  The engine uses three levels of evidence:
    Step 1 — Symptoms         (priority 7, strong but not conclusive)
    Step 2 — Lab test results (priority 9, highest trust)
    Step 3 — Clinical judgement (priority 6, supporting opinion)
""")

    base = BeliefBase(BACKGROUND)

    # --- Symptom observations ---
    _separator()
    print("  STEP 1: Observed symptoms")
    print("  Look at the patient and answer what you can observe directly.\n")

    symptom_questions = [
        (fever,       "Fever",       "Does the patient have a fever?",
                      "A temperature above 38°C counts as a fever."),
        (cough,       "Cough",       "Does the patient have a cough?",
                      "Any persistent cough, dry or wet."),
        (fatigue,     "Fatigue",     "Does the patient report fatigue?",
                      "Unusual tiredness or low energy reported by the patient."),
        (sore_throat, "Sore throat", "Does the patient have a sore throat?",
                      "Pain or irritation in the throat, especially when swallowing."),
    ]

    for atom, name, question, hint in symptom_questions:
        print(f"  [{name}]  {hint}")
        ans = _ask(question)
        if ans is True:
            base = revise(base, atom,      priority=7)
        elif ans is False:
            base = revise(base, Not(atom), priority=7)
        print()

    _print_diagnosis(base)

    # --- Lab / test results ---
    _separator()
    print("  STEP 2: Lab test results")
    print("  Enter any test results you have. These carry the highest weight.\n")

    test_questions = [
        (flu,   "Flu test",   "Flu test result — was it positive?",
                "A positive rapid flu test confirms influenza."),
        (covid, "COVID test", "COVID test result — was it positive?",
                "A positive lateral flow or PCR test confirms COVID-19."),
    ]

    for atom, name, question, hint in test_questions:
        print(f"  [{name}]  {hint}")
        ans = _ask(question)
        if ans is True:
            base = revise(base, atom,      priority=9)
        elif ans is False:
            base = revise(base, Not(atom), priority=9)
        print()

    _print_diagnosis(base)

    # --- Doctor's clinical judgement ---
    _separator()
    print("  STEP 3: Clinical judgement")
    print("  Your overall professional assessment of the patient.\n")

    clinical_questions = [
        (healthy, "Overall health", "Does the patient appear healthy overall?",
                  "No signs of illness — patient seems well despite any mild symptoms."),
        (cold,    "Common cold",    "Does the presentation suggest a common cold?",
                  "Mild symptoms, no fever, consistent with a rhinovirus infection."),
    ]

    for atom, name, question, hint in clinical_questions:
        print(f"  [{name}]  {hint}")
        ans = _ask(question)
        if ans is True:
            base = revise(base, atom,      priority=6)
        elif ans is False:
            base = revise(base, Not(atom), priority=6)
        print()

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
