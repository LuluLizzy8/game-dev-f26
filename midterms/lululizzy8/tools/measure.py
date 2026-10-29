"""Legal-list sizes, deal length and prompt sizes, measured on non-held-out seeds only (0-104).

    python tools/measure.py
No model calls. Token counts are estimated as characters / 4.
"""
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from doudizhu.engine import DouDizhu  # noqa: E402
from players import heuristic  # noqa: E402
from players.model import SYSTEM_PROMPT, build_prompt  # noqa: E402

SEEDS = range(0, 105)
assert max(SEEDS) < 200, "never measure held-out seeds before the freeze"


def main():
    opening, steps, decisions = [], [], []
    prompt_tokens = {"model-history": [], "model-obs": []}
    for seed in SEEDS:
        g = DouDizhu()
        g.reset(seed)
        opening.append(len(g.legal_actions(g.turn)))
        per_seat = [0, 0, 0]
        while g.outcome()["status"] == "ongoing":
            seat = g.turn
            obs, legal = g.observe(seat), g.legal_actions(seat)
            if len(legal) > 1:
                per_seat[seat] += 1
                for variant in prompt_tokens:
                    prompt_tokens[variant].append((len(SYSTEM_PROMPT) + len(build_prompt(obs, legal, variant))) / 4)
            g.step(seat, heuristic.choose(obs, legal))
        steps.append(g.steps)
        decisions += per_seat

    def stats(xs):
        return f"median {statistics.median(xs):.0f}, max {max(xs):.0f}"

    print(f"Seeds {SEEDS.start}-{SEEDS.stop - 1}, all seats heuristic.")
    print(f"Opening legal-list size: {stats(opening)}")
    print(f"Steps per deal: {stats(steps)}")
    print(f"Non-forced decisions per seat per deal: {stats(decisions)}")
    for variant, xs in prompt_tokens.items():
        print(f"Estimated input tokens per call, {variant}: {stats(xs)}")


if __name__ == "__main__":
    main()
