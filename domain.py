"""
domain.py
---------
Medical diagnosis domain for the belief revision engine.

Atoms:
  fever, cough, fatigue, sore_throat  -- symptoms
  flu, covid, cold, healthy           -- conditions

Priority scale (1-10):
  9-10  medical laws / background knowledge (almost never dropped)
  5-7   strong clinical evidence
  2-4   initial working hypothesis (readily revised)
  1     weak suspicion
"""

from formula import Atom, Implies, Not, And, Or, Iff

# ---------------------------------------------------------------------------
# Atoms
# ---------------------------------------------------------------------------

# Symptoms
fever       = Atom('fever')
cough       = Atom('cough')
fatigue     = Atom('fatigue')
sore_throat = Atom('sore_throat')

# Conditions
flu     = Atom('flu')
covid   = Atom('covid')
cold    = Atom('cold')
healthy = Atom('healthy')


# ---------------------------------------------------------------------------
# Initial belief base
# Each entry is (formula, priority)
# ---------------------------------------------------------------------------

INITIAL_BELIEFS = [

    # --- Background knowledge (priority 9-10) ---
    # These are medical "laws" — the engine should almost never drop these

    (Implies(flu,   And(fever, cough)),      10),  # flu → fever ∧ cough
    (Implies(covid, And(fever, fatigue)),    10),  # covid → fever ∧ fatigue
    (Implies(cold,  And(cough, sore_throat)), 10), # cold → cough ∧ sore_throat
    (Implies(healthy, Not(fever)),           10),  # healthy → ¬fever
    (Implies(healthy, Not(cough)),           10),  # healthy → ¬cough

    # A patient can only have one condition at a time (simplification)
    (Implies(flu,   Not(covid)),             9),
    (Implies(flu,   Not(cold)),              9),
    (Implies(covid, Not(flu)),               9),
    (Implies(covid, Not(cold)),              9),

    # --- Strong clinical evidence (priority 5-7) ---
    # Observed symptoms for this specific patient

    (fever,       6),  # patient has a fever
    (cough,       6),  # patient has a cough
    (fatigue,     5),  # patient reports fatigue

    # --- Working hypothesis (priority 2-4) ---
    # Initial guess before test results come in

    (flu,         3),  # working diagnosis: flu
]


# ---------------------------------------------------------------------------
# Revision scenarios
# Each scenario is (description, formula_to_revise_with)
# ---------------------------------------------------------------------------

SCENARIOS = [
    (
        "Flu test comes back negative",
        Not(flu),
        # Expected: flu dropped, covid becomes more plausible (fever + fatigue match)
    ),
    (
        "Covid test comes back positive",
        covid,
        # Expected: flu dropped (mutual exclusion), covid added
    ),
    (
        "Patient recovers — no more fever",
        Not(fever),
        # Expected: flu and covid hypotheses dropped or weakened
    ),
    (
        "Doctor confirms patient is healthy",
        healthy,
        # Expected: fever, cough, flu, covid all need to go (conflict with healthy → ¬fever)
    ),
    (
        "Sore throat observed",
        sore_throat,
        # Expected: cold becomes a candidate (cold → cough ∧ sore_throat)
    ),
]


# ---------------------------------------------------------------------------
# AGM postulate test cases
# These are (belief_base_formulas, revision_formula, description)
# ---------------------------------------------------------------------------

AGM_TESTS = [
    {
        "postulate": "Success",
        "description": "After revising with φ, φ must be in the result",
        "base": [flu, Implies(flu, fever), fever],
        "revise_with": Not(flu),
        # Check: Not(flu) must be in the revised base
    },
    {
        "postulate": "Vacuity",
        "description": "If ¬φ was not believed, revision = expansion",
        "base": [fever, cough],       # does NOT contain Not(covid)
        "revise_with": covid,
        # Check: result should equal base + {covid}
    },
    {
        "postulate": "Consistency",
        "description": "Revised base must be consistent (unless φ is a contradiction)",
        "base": [flu, Implies(flu, fever), fever],
        "revise_with": Not(fever),
        # Check: result is satisfiable
    },
    {
        "postulate": "Inclusion",
        "description": "B * φ ⊆ B + φ  (revision doesn't add more than expansion)",
        "base": [flu, Implies(flu, fever)],
        "revise_with": Not(flu),
        # Check: every formula in revised base is also in expanded base
    },
    {
        "postulate": "Extensionality",
        "description": "If φ ↔ ψ is a tautology, then B*φ = B*ψ",
        "base": [flu, fever],
        # p ∨ q  is logically equivalent to  q ∨ p
        "revise_with": Or(Not(flu), Not(fever)),
        "revise_with_equivalent": Or(Not(fever), Not(flu)),
        # Check: both revisions produce identical bases
    },
]


# ---------------------------------------------------------------------------
# Pretty printer
# ---------------------------------------------------------------------------

def print_belief_base(beliefs: list, label: str = "Belief base"):
    print(f"\n{'='*50}")
    print(f"  {label}")
    print(f"{'='*50}")
    for formula, priority in sorted(beliefs, key=lambda x: -x[1]):
        print(f"  [{priority:2d}]  {formula}")
    print()


if __name__ == "__main__":
    print_belief_base(INITIAL_BELIEFS, "Initial medical belief base")

    print("Revision scenarios:")
    for i, (desc, formula, *_) in enumerate(SCENARIOS, 1):
        print(f"  {i}. {desc}")
        print(f"     Revise with: {formula}\n")
