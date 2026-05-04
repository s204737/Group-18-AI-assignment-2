# Belief Revision Engine
02180 Introduction to AI, Assignment 2 (Group 18)

## Overview

A belief revision engine implemented in Python using propositional logic. The agent maintains a prioritised belief base and revises it when new information arrives, following the AGM framework. A weather forecasting domain is used as the running example.

## Requirements

Python 3.10 or higher. No external packages required.

## How to Run

By default, `main.py` runs the AGM postulate test suite:

```bash
python main.py
```

Modes:

```bash
python main.py --tests       # AGM postulate tests (default)
python main.py --weather     # interactive weather forecasting demo
```

### Interactive weather demo

```bash
python main.py --weather
```

A guided session where the user enters current observations and instrument readings. The belief base is revised after each input and a forecast is produced.

The interface has three stages:
- **Step 1, Current conditions** (priority 7): rain, wind, cloud, snow
- **Step 2, Instrument readings** (priority 8): temperature, barometer
- **Step 3, Additional judgement** (priority 6): storm, frost, clear skies

Answer `y`, `n`, or `?` (skip) to each question.

## File Structure

| File | Purpose |
|---|---|
| `formula.py` | Propositional logic AST (Atom, Not, And, Or, Implies, Iff) and CNF conversion |
| `belief_base.py` | Prioritised belief base, stores (formula, priority) pairs |
| `entailment.py` | Resolution-based logical entailment (no external packages) |
| `operations.py` | Expansion and partial meet contraction |
| `revision.py` | Belief revision via the Levi Identity: B * φ = (B ÷ ¬φ) + φ |
| `weather.py` | Interactive weather forecasting demo |
| `agm_tests.py` | Tests for all 5 AGM postulates |
| `main.py` | Entry point |

## Implementation Summary

### Belief Base
Beliefs are stored as `(formula, priority)` pairs where higher priority means more entrenched. When new information conflicts with existing beliefs, lower-priority beliefs are dropped first.

### Entailment
Uses resolution refutation: to check `KB |= φ`, the engine negates φ, converts `KB ∪ {¬φ}` to CNF, and applies the resolution rule until the empty clause is derived (entailed) or no new clauses can be produced (not entailed).

CNF conversion follows the standard pipeline: eliminate `↔`, eliminate `→`, push negations inward via De Morgan, and distribute `∨` over `∧`.

### Contraction `B ÷ φ`
Partial meet contraction: finds all maximal subsets of B that do not entail φ (the remainder set `B ⊥ φ`), then a priority-based selection function picks the remainder(s) with the highest total priority score, and returns their intersection.

### Expansion `B + φ`
Adds φ to the belief base at the given priority. Purely syntactic, no consistency check.

### Revision `B * φ`
Implemented via the Levi Identity:
```
B * φ  =  (B ÷ ¬φ) + φ
```
First contract by ¬φ to remove conflicting beliefs, then expand with φ.

### AGM Postulates
All 5 mandatory revision postulates are verified, each using a distinct weather scenario:

| Postulate | Scenario | What it checks |
|---|---|---|
| Success | Storm forecast revised with ¬storm | φ is in B * φ |
| Inclusion | Storm expected, satellite confirms clear | B * φ ⊆ B + φ |
| Vacuity | Base has no opinion on frost | If ¬φ ∉ B then B * φ = B + φ |
| Consistency | Frost forecast revised with rain | B * φ is satisfiable |
| Extensionality | Two logically equivalent disjunctions | If φ ↔ ψ is a tautology then B * φ = B * ψ |

Run `python main.py --tests` to execute the suite.
