# Belief Revision Engine
02180 Introduction to AI — Assignment 2

## Overview

A belief revision engine implemented in Python using propositional logic. The agent maintains a prioritised belief base and revises it when new information arrives, following the AGM framework. A medical diagnosis domain is used as the running example.

## Requirements

Python 3.10 or higher. No external packages required.

## How to Run

### Full demo (recommended starting point)
```bash
python main.py
```
Runs three things in sequence:
1. A focused single revision example (flu test comes back negative)
2. A full medical scenario demo with 5 sequential revisions
3. The AGM postulate test suite

### Individual modes
```bash
python main.py --single       # focused single revision example only
python main.py --demo         # 5 medical scenarios only
python main.py --tests        # AGM postulate tests only
python main.py --doctor       # interactive doctor interface
```

### Interactive doctor interface
```bash
python main.py --doctor
# or
python doctor.py
```
A guided step-by-step interface where you answer questions about a patient's symptoms and test results. The belief base is revised after each answer and a final diagnosis is produced.

## File Structure

| File | Purpose |
|---|---|
| `formula.py` | Propositional logic AST (Atom, Not, And, Or, Implies, Iff) and CNF conversion |
| `belief_base.py` | Prioritised belief base — stores (formula, priority) pairs |
| `entailment.py` | Resolution-based logical entailment (no external packages) |
| `operations.py` | Expansion and partial meet contraction |
| `revision.py` | Belief revision via the Levi Identity: B * φ = (B ÷ ¬φ) + φ |
| `domain.py` | Medical diagnosis domain — atoms, initial beliefs, scenarios |
| `agm_tests.py` | Tests for all 5 AGM postulates |
| `main.py` | Entry point |
| `doctor.py` | Interactive diagnostic interface |
| `cli.py` | General-purpose formula REPL (optional) |

## Implementation Summary

### Belief Base
Beliefs are stored as `(formula, priority)` pairs where higher priority means more entrenched. When new information conflicts with existing beliefs, lower-priority beliefs are dropped first.

### Entailment
Uses resolution refutation: to check `KB |= φ`, the engine negates φ, converts `KB ∪ {¬φ}` to CNF, and applies the resolution rule until the empty clause is derived (entailed) or no new clauses can be produced (not entailed).

### Contraction  `B ÷ φ`
Partial meet contraction: finds all maximal subsets of B that do not entail φ (remainder sets), then selects the one(s) with the highest total priority score, and returns their intersection.

### Expansion  `B + φ`
Simply adds φ to the belief base at the given priority.

### Revision  `B * φ`
Implemented via the Levi Identity:
```
B * φ  =  (B ÷ ¬φ) + φ
```
First contract by ¬φ to remove conflicting beliefs, then expand with φ.

### AGM Postulates
All 5 mandatory postulates are verified:

| Postulate | What it checks |
|---|---|
| Success | φ is in B * φ |
| Inclusion | B * φ ⊆ B + φ |
| Vacuity | If ¬φ ∉ B then B * φ = B + φ |
| Consistency | B * φ is satisfiable (unless φ is a contradiction) |
| Extensionality | If φ ↔ ψ is a tautology then B * φ = B * ψ |
