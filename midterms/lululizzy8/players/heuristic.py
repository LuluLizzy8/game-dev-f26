"""Rule-based baseline (GAME-DESIGN.md §4.1). Deterministic; uses only the seat's observation and legal list.

Developed on seeds 0-99 only.
"""
from doudizhu.engine import REVOLUTION_BOMB, TWO, all_moves, parse, strength

BOMBS = ("bomb", "rocket")


def wants_flip(hand, revolution):
    """R10b: flip the order when most of these 3-2 cards are stronger the other way."""
    plain = [c for c in hand if c <= TWO]
    low = sum(c <= 9 for c in plain)
    return (low > len(plain) - low) != revolution


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

    rev = obs.get("revolution", False)

    def key(rank):
        return strength(rank, rev)

    beat = obs["to_beat"]
    teammate_play = obs["teammate"] is not None and beat is not None and beat["seat"] == obs["teammate"]
    flips = [a for a in plays if combos[a].kind == "bomb" and combos[a].length >= REVOLUTION_BOMB]
    if flips and not teammate_play:  # start or end a revolution when the rest of the hand gains from it
        flip = min(flips, key=lambda a: (combos[a].length, key(combos[a].rank)))
        rest = list(hand)
        for c in parse(flip):
            rest.remove(c)
        if wants_flip(rest, rev):
            return flip

    me, landlord = obs["seat"], obs["landlord"]
    opponents = [s for s in range(3) if s != me and (me == landlord or s == landlord)]
    danger = min(obs["cards_left"][s] for s in opponents) <= 4
    normal = [a for a in plays if combos[a].kind not in BOMBS]
    bombs = [a for a in plays if combos[a].kind in BOMBS]

    def cost(a):
        cards = parse(a)
        # lowest main rank first; then shed more cards; then keep high kickers
        return key(combos[a].rank), -len(cards), max(map(key, cards)), sum(map(key, cards))

    if beat is None:  # lead
        return min(normal or bombs, key=cost)
    if teammate_play:
        return "pass"  # do not overtake the teammate
    if normal:
        return min(normal, key=lambda a: (key(combos[a].rank), sum(map(key, parse(a)))))
    if bombs and danger:
        return min(bombs, key=lambda a: (combos[a].kind == "rocket", combos[a].length, key(combos[a].rank)))  # smallest bomb first
    return "pass"
