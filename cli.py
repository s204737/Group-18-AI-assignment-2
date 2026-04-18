"""
cli.py
------
Interactive REPL for the belief revision engine.

Formula syntax
--------------
  Atoms         : any word, e.g.  flu  fever  sore_throat
  Negation      : not <φ>   or   !<φ>
  Conjunction   : <φ> and <ψ>
  Disjunction   : <φ> or  <ψ>
  Implication   : <φ> -> <ψ>
  Biconditional : <φ> <-> <ψ>
  Grouping      : ( <φ> )

Precedence (lowest → highest): <->, ->, or, and, not, atom/(...)

Commands
--------
  show              display the current belief base
  expand <φ> [p]    add φ with optional priority p  (default 5)
  contract <φ>      contract by φ
  revise <φ> [p]    revise with φ using Levi Identity (default priority 5)
  entails <φ>       check whether the base entails φ
  consistent        check whether the base is consistent
  reset             restore the initial belief base from domain.py
  atoms             list atom names seen so far
  help              show this help
  quit / exit       exit
"""

import re
import sys

from formula import Atom, Not, And, Or, Implies, Iff, Formula
from belief_base import BeliefBase
from operations import expand, contract
from revision import revise as levi_revise
from entailment import entails, is_consistent
from domain import INITIAL_BELIEFS, print_belief_base


# ---------------------------------------------------------------------------
# Formula parser
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r'<->|->|[()!]|[a-zA-Z_][a-zA-Z0-9_]*')


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text)


class _Parser:
    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> str | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self) -> str:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, val: str) -> None:
        tok = self.peek()
        if tok != val:
            raise ValueError(f"Expected '{val}', got '{tok}'")
        self.consume()

    # -- grammar (lowest to highest precedence) --

    def parse_iff(self) -> Formula:
        left = self.parse_implies()
        while self.peek() == '<->':
            self.consume()
            left = Iff(left, self.parse_implies())
        return left

    def parse_implies(self) -> Formula:
        left = self.parse_or()
        while self.peek() == '->':
            self.consume()
            left = Implies(left, self.parse_or())
        return left

    def parse_or(self) -> Formula:
        left = self.parse_and()
        while self.peek() == 'or':
            self.consume()
            left = Or(left, self.parse_and())
        return left

    def parse_and(self) -> Formula:
        left = self.parse_not()
        while self.peek() == 'and':
            self.consume()
            left = And(left, self.parse_not())
        return left

    def parse_not(self) -> Formula:
        if self.peek() in ('not', '!'):
            self.consume()
            return Not(self.parse_not())
        return self.parse_primary()

    def parse_primary(self) -> Formula:
        tok = self.peek()
        if tok is None:
            raise ValueError("Unexpected end of formula")
        if tok == '(':
            self.consume()
            expr = self.parse_iff()
            self.expect(')')
            return expr
        if tok in ('not', '!', '->', '<->', 'or', 'and', ')'):
            raise ValueError(f"Unexpected token '{tok}' where an atom was expected")
        self.consume()
        return Atom(tok)


def parse_formula(text: str) -> Formula:
    tokens = _tokenize(text)
    if not tokens:
        raise ValueError("Empty formula")
    parser = _Parser(tokens)
    result = parser.parse_iff()
    if parser.pos != len(parser.tokens):
        leftover = ' '.join(parser.tokens[parser.pos:])
        raise ValueError(f"Unexpected leftover input: '{leftover}'")
    return result


# ---------------------------------------------------------------------------
# REPL helpers
# ---------------------------------------------------------------------------

def _display(base: BeliefBase) -> None:
    beliefs = list(base)
    if not beliefs:
        print("  (belief base is empty)")
        return
    print_belief_base(beliefs, "Current belief base")


def _atoms_seen(base: BeliefBase) -> set[str]:
    result: set[str] = set()
    for f, _ in base:
        result |= f.atoms()
    return result


def _parse_formula_and_priority(parts: list[str], default_priority: int = 5):
    """
    Split a token list into (formula_text, priority).
    If the last token is an integer it's treated as the priority.
    """
    if not parts:
        raise ValueError("No formula provided")
    if parts and parts[-1].lstrip('-').isdigit():
        priority = int(parts[-1])
        formula_text = ' '.join(parts[:-1])
    else:
        priority = default_priority
        formula_text = ' '.join(parts)
    return parse_formula(formula_text), priority


HELP_TEXT = __doc__


# ---------------------------------------------------------------------------
# Main REPL
# ---------------------------------------------------------------------------

def run_cli() -> None:
    print("\n" + "=" * 58)
    print("  Belief Revision Engine — Interactive Mode")
    print("  Type  help  for commands,  quit  to exit.")
    print("=" * 58)

    base = BeliefBase(INITIAL_BELIEFS)
    _display(base)

    while True:
        try:
            raw = input("br> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye.")
            break

        if not raw:
            continue

        parts = raw.split()
        cmd, rest = parts[0].lower(), parts[1:]

        try:
            if cmd in ('quit', 'exit'):
                print("Bye.")
                break

            elif cmd == 'help':
                print(HELP_TEXT)

            elif cmd == 'show':
                _display(base)

            elif cmd == 'atoms':
                atoms = _atoms_seen(base)
                print("  Atoms in current base:", ', '.join(sorted(atoms)) or '(none)')

            elif cmd == 'consistent':
                result = is_consistent(base.formulas())
                print(f"  Consistent: {result}")

            elif cmd == 'reset':
                base = BeliefBase(INITIAL_BELIEFS)
                print("  Belief base reset to initial domain state.")
                _display(base)

            elif cmd == 'expand':
                phi, priority = _parse_formula_and_priority(rest)
                base = expand(base, phi, priority)
                print(f"  Expanded with {phi}  [priority {priority}]")
                _display(base)

            elif cmd == 'contract':
                phi = parse_formula(' '.join(rest))
                base = contract(base, phi)
                print(f"  Contracted by {phi}")
                _display(base)

            elif cmd == 'revise':
                phi, priority = _parse_formula_and_priority(rest)
                base = levi_revise(base, phi, priority)
                print(f"  Revised with {phi}  [priority {priority}]")
                _display(base)

            elif cmd == 'entails':
                phi = parse_formula(' '.join(rest))
                result = entails(base.formulas(), phi)
                print(f"  Base entails {phi}: {result}")

            else:
                print(f"  Unknown command '{cmd}'. Type  help  for the list.")

        except ValueError as exc:
            print(f"  Parse error: {exc}")
        except Exception as exc:
            print(f"  Error: {exc}")


if __name__ == "__main__":
    run_cli()
