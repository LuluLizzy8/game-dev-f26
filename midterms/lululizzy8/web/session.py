"""Browser play, same setup as play.py: you take one seat, two heuristic players take the others.

web/index.html loads this file, the engine and the heuristic into Pyodide and calls Session.
Every reply is JSON built only from observe(your seat), so the page never sees another hand (R15).
"""
import json

from doudizhu.engine import DouDizhu, all_moves, label, parse
from players import heuristic

NAMES = {"single": "a single", "pair": "a pair", "triple": "a triple", "triple+1": "a triple with one single",
         "triple+2": "a triple with a pair", "four+2": "four of a kind with two singles",
         "four+2pairs": "four of a kind with two pairs", "rocket": "the rocket"}


def describe(combo):
    """Plain words for a combination, e.g. 'a 6-card straight'."""
    n = combo.length
    return NAMES.get(combo.kind) or {
        "bomb": f"a {n}-card bomb", "straight": f"a {n}-card straight", "pair_seq": f"{n} pairs in a row",
        "plane": f"{n} triples in a row", "plane+1": f"{n} triples in a row with {n} singles",
        "plane+2": f"{n} triples in a row with {n} pairs"}[combo.kind]


def combo_of(cards):
    """The one combination these exact cards make, or None."""
    ranks = parse(cards)
    return all_moves(ranks).get(label(ranks))


def seed_with_landlord(seat, start):
    """The first seed from start whose deal makes this seat landlord (R4: the seed picks the landlord).

    The page uses it to rotate the landlord between deals without changing the rules.
    """
    g, seed = DouDizhu(), start
    while g.reset(seed) and g.landlord != seat:
        seed += 1
    return seed


class Session:
    def __init__(self, seed, seat, watch=False):
        """watch=True: the heuristic plays your seat too, and the page shows the deal from your seat."""
        self.g = DouDizhu()
        self.g.reset(seed)
        self.seat = seat
        self.watch = watch

    def _bots(self):
        """Play the other seats until it is your turn or the deal ends; one frame per move for the page."""
        g, frames = self.g, []
        while g.outcome()["status"] == "ongoing" and (self.watch or g.turn != self.seat):
            s = g.turn
            g.step(s, heuristic.choose(g.observe(s), g.legal_actions(s)))
            frames.append(g.observe(self.seat))
        return frames

    def _reply(self, frames, **extra):
        g = self.g
        return json.dumps(dict(extra, frames=frames, obs=g.observe(self.seat),
                               legal=g.legal_actions(self.seat), outcome=g.outcome()), ensure_ascii=False)

    def start(self):
        """The deal before any move (frame 0), then the moves up to your turn."""
        return self._reply([self.g.observe(self.seat), *self._bots()], ok=True)

    def play(self, action):
        """Your move as card text in any order ("3 3", "bj bj rj rj") or "pass". A refused move changes nothing."""
        result = self.g.step(self.seat, action)
        if not result["ok"]:
            return self._reply([], ok=False, error=self.explain(action))
        return self._reply([self.g.observe(self.seat), *self._bots()], ok=True)

    def hint(self):
        """What the heuristic would play from your seat, or None when it is not your turn."""
        legal = self.g.legal_actions(self.seat)
        return heuristic.choose(self.g.observe(self.seat), legal) if legal else None

    def explain(self, action):
        """Why a move is refused, in plain words; None if it is legal."""
        g, obs = self.g, self.g.observe(self.seat)
        legal = g.legal_actions(self.seat)
        if not legal:
            return "It is not your turn."
        if action.strip().lower() == "pass":
            return None if "pass" in legal else "You have the lead, so you must play something."
        try:
            mine = combo_of(action)
        except KeyError:
            return "Those are not cards."
        if mine is None:
            return f"{label(parse(action))} is not a combination. The handbook lists every combination."
        if label(parse(action)) in legal:
            return None
        if obs["to_beat"] is None:
            return "You do not hold those cards."
        tb = combo_of(obs["to_beat"]["cards"])
        if tb.kind == "rocket":
            return "Nothing beats the rocket. Pass."
        flipped = " In a revolution the order is reversed: 3 is highest, 2 lowest." if obs["revolution"] else ""
        if mine.kind == "bomb" and tb.kind == "bomb":
            return f"Your {describe(mine)} must have more cards than {describe(tb)}, or as many cards of a higher rank.{flipped}"
        if (mine.kind, mine.length) != (tb.kind, tb.length):
            return f"You chose {describe(mine)}. To follow {describe(tb)}, play {describe(tb)} that ranks higher, a bomb, or the rocket."
        return f"Your {describe(mine)} does not rank higher than {obs['to_beat']['cards']}.{flipped}"
