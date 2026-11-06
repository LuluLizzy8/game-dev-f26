"""Rule-based baseline (DESIGN.md §4.1). Deterministic; uses only the seat's observation and legal list.

Developed on seeds 0-99 only.
"""
from doudizhu.engine import all_moves, parse

BOMBS = ("bomb", "rocket")


def choose(obs, legal):
    plays = [a for a in legal if a != "pass"]
    if not plays:
        return "pass"
    hand = parse(obs["hand"])
    combos = all_moves(hand)
    # Endgame: go out if one play empties the hand.
    for a in plays:
        if len(a.split()) == len(hand):
            return a

    me, landlord = obs["seat"], obs["landlord"]
    opponents = [s for s in range(3) if s != me and (me == landlord or s == landlord)]
    danger = min(obs["cards_left"][s] for s in opponents) <= 4
    normal = [a for a in plays if combos[a].kind not in BOMBS]
    bombs = [a for a in plays if combos[a].kind in BOMBS]

    def cost(a):
        cards = parse(a)
        # lowest main rank first; then shed more cards; then keep high kickers
        return combos[a].rank, -len(cards), max(cards), sum(cards)

    beat = obs["to_beat"]
    if beat is None:  # lead
        return min(normal or bombs, key=cost)
    if obs["teammate"] is not None and beat["seat"] == obs["teammate"]:
        return "pass"  # do not overtake the teammate
    if normal:
        return min(normal, key=lambda a: (combos[a].rank, sum(parse(a))))
    if bombs and danger:
        return min(bombs, key=lambda a: (combos[a].kind == "rocket", combos[a].length, combos[a].rank))  # smallest bomb first
    return "pass"
