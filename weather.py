"""
Practicel Test: Weather forecasting using the belief revision engine.

The user enters current observations and instrument readings.
The belief base is revised after each input and a forecast is produced.
"""

from formula import Atom, Not, Implies, And
from belief_base import BeliefBase
from revision import revise
from entailment import entails


# ----------------Atoms--------------------------

rain         = Atom('rain')
wind         = Atom('wind')
cloud        = Atom('cloud')
snow         = Atom('snow')
low_temp     = Atom('low_temp')
pressure_drop = Atom('pressure_drop')
storm        = Atom('storm')
clear        = Atom('clear')
frost        = Atom('frost')

FORECASTS = {
    storm: "Storm",
    clear: "Clear",
    frost: "Frost",
}


# ----------------Background knowledge / Initial Beliefs----------------------

BACKGROUND = [
    # Storm conditions
    (Implies(storm, And(rain, wind)),   10),
    (Implies(storm, cloud),             10),
    (Implies(storm, Not(clear)),        10),
    (Implies(storm, Not(frost)),        10),

    # Clear conditions
    (Implies(clear, Not(rain)),         10),
    (Implies(clear, Not(cloud)),        10),
    (Implies(clear, Not(storm)),        10),

    # Frost conditions
    (Implies(frost, low_temp),          10),
    (Implies(frost, Not(rain)),         10),
    (Implies(frost, Not(storm)),        10),

    # Snow requires cold
    (Implies(snow, low_temp),           10),

    # Falling pressure indicates storm
    (Implies(pressure_drop, storm),      8),
]

# --------------Helper Functions----------------------

def _ask(question: str) -> bool | None:
    while True:
        ans = input(f"  {question} [y/n/?]: ").strip().lower()
        if ans in ('y', 'yes'):   return True
        if ans in ('n', 'no'):    return False
        if ans in ('?', ''):      return None
        print("  Enter y, n, or ? to skip.")


def _print_forecast(base: BeliefBase) -> None:
    formulas = base.formulas()
    results = [name for atom, name in FORECASTS.items() if entails(formulas, atom)]
    if results:
        print("  Forecast: " + ",  ".join(results))
    else:
        print("  Forecast: No severe weather")
    print()


# -----------------Main function---------------------

def run_weather() -> None:
    print("\nWeather Forecast — Belief Revision Engine")
    print("─" * 42)
    print("Answer y / n / ? (unknown) for each reading.\n")

    base = BeliefBase(BACKGROUND)

    print("Current conditions:")
    for atom, question in [
        (rain,      "Raining?"),
        (wind,      "Strong wind?"),
        (cloud,     "Overcast?"),
        (snow,      "Snowing?"),
    ]:
        ans = _ask(question)
        if ans is True:
            base = revise(base, atom,      priority=7)
        elif ans is False:
            base = revise(base, Not(atom), priority=7)

    print()
    _print_forecast(base)

    print("Instrument readings:")
    for atom, question in [
        (low_temp,      "Temperature below 5°C?"),
        (pressure_drop, "Barometer dropping?"),
    ]:
        ans = _ask(question)
        if ans is True:
            base = revise(base, atom,      priority=8)
        elif ans is False:
            base = revise(base, Not(atom), priority=8)

    print()
    _print_forecast(base)

    print("Additional judgement:")
    for atom, question in [
        (storm, "Storm likely?"),
        (frost,  "Frost overnight?"),
        (clear,  "Clear skies expected?"),
    ]:
        ans = _ask(question)
        if ans is True:
            base = revise(base, atom,      priority=6)
        elif ans is False:
            base = revise(base, Not(atom), priority=6)

    print()
    print("─" * 42)
    print("FINAL FORECAST")
    print("─" * 42)
    _print_forecast(base)


if __name__ == "__main__":
    run_weather()
