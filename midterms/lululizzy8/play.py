"""Human play: you take one seat, two heuristic players take the others.

    python play.py --seat 0 --seed 7
"""
import argparse

from doudizhu.engine import DouDizhu
from doudizhu.view import render
from players import heuristic
from players.model import normalize


def ask(legal):
    while True:
        try:
            text = input("Your move (number or cards, e.g. 1 or '3 3'): ").strip()
        except EOFError:
            raise SystemExit("\nInput closed; the deal was not finished.")
        if text.isdigit() and 1 <= int(text) <= len(legal):
            return legal[int(text) - 1]
        action = normalize(text, legal)
        if action:
            return action
        print(f"  {text!r} is not a legal action now. Pick a number from the list.")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--seat", type=int, choices=(0, 1, 2), default=0)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args(argv)

    g = DouDizhu()
    g.reset(args.seed)
    me = args.seat
    print(f"Seed {args.seed}. You are seat {me}; the landlord is seat {g.landlord}.\n")
    while g.outcome()["status"] == "ongoing":
        seat = g.turn
        obs, legal = g.observe(seat), g.legal_actions(seat)
        if seat == me:
            print("\n" + render(obs) + "\n\nLegal actions:")
            for i, a in enumerate(legal, 1):
                print(f"  {i}. {a}")
            action = ask(legal)
        else:
            action = heuristic.choose(obs, legal)
        g.step(seat, action)
        print(f"> seat {seat}{' (you)' if seat == me else ''}: {action}")
    out = g.outcome()
    print("\n" + render(g.observe(me)))
    print(f"\nResult: {out['winner']} win ({out['reason']}). Multiplier x{out['multiplier']}"
          f"{', spring' if out['spring'] else ''}. Scores by seat: {out['scores']}. Your score: {out['scores'][me]}.")


if __name__ == "__main__":
    main()
