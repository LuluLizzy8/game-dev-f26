"""Dou Dizhu with two decks (108 cards), three players, one deal, landlord chosen by seed. Rule numbers (R1...) refer to the README map."""
import random
from collections import Counter, namedtuple
from itertools import combinations

# R2: cards are rank numbers; suits are not tracked (R1a).
LABELS = {r: str(r) for r in range(3, 11)}
LABELS.update({11: "J", 12: "Q", 13: "K", 14: "A", 15: "2", 16: "BJ", 17: "RJ"})
RANKS = {v: k for k, v in LABELS.items()}
ACE, TWO, BLACK_JOKER, RED_JOKER = 14, 15, 16, 17

# rank: the lowest main rank (a triple's rank, a sequence's first card); length: sequence length.
Combo = namedtuple("Combo", "kind rank length")


def label(cards):
    return " ".join(LABELS[c] for c in sorted(cards))


def parse(text):
    """Card list text -> sorted ranks. Raises KeyError on an unknown card."""
    return sorted(RANKS[t] for t in text.upper().split())


def all_moves(hand):
    """R7, R8: every combination the hand can play, as {label: Combo}."""
    count = Counter(hand)
    ranks = sorted(count)
    moves = {}

    def add(kind, rank, length, cards):
        combo = Combo(kind, rank, length)
        assert moves.setdefault(label(cards), combo) == combo, label(cards)

    for r in ranks:
        add("single", r, 1, [r])
        others = [k for k in ranks if k != r]
        if count[r] >= 2:
            add("pair", r, 1, [r] * 2)
        if count[r] >= 3:
            add("triple", r, 1, [r] * 3)
            for k in others:
                add("triple+1", r, 1, [r] * 3 + [k])
                if count[k] >= 2:
                    add("triple+2", r, 1, [r] * 3 + [k] * 2)
        for n in range(4, count[r] + 1):  # R10a: two decks, so a bomb is 4 to 8 of a rank
            add("bomb", r, n, [r] * n)
        if count[r] >= 4:
            for a, b in combinations(others, 2):
                add("four+2", r, 1, [r] * 4 + [a, b])
                if count[a] >= 2 and count[b] >= 2:
                    add("four+2pairs", r, 1, [r] * 4 + [a] * 2 + [b] * 2)
    if count[BLACK_JOKER] == 2 and count[RED_JOKER] == 2:  # R10a: the rocket is all four jokers
        add("rocket", BLACK_JOKER, 4, [BLACK_JOKER] * 2 + [RED_JOKER] * 2)

    for kind, width, min_len in (("straight", 1, 5), ("pair_seq", 2, 3), ("plane", 3, 2)):
        for start in range(3, ACE + 1):
            end = start
            while end <= ACE and count[end] >= width:
                end += 1
                length = end - start
                if length < min_len:
                    continue
                body = [r for r in range(start, end) for _ in range(width)]
                add(kind, start, length, body)
                if kind == "plane":
                    outside = [k for k in ranks if not start <= k < end]
                    for wings in combinations(outside, length):
                        add("plane+1", start, length, body + list(wings))
                        if all(count[k] >= 2 for k in wings):
                            add("plane+2", start, length, body + [k for k in wings for _ in range(2)])
    return moves


def beats(a, b):
    """R9, R10, R10a: does combination a beat combination b?"""
    if a.kind == "rocket":
        return True
    if b.kind == "rocket":
        return False
    if a.kind == "bomb":  # more cards first, then rank
        return b.kind != "bomb" or (a.length, a.rank) > (b.length, b.rank)
    return a.kind == b.kind and a.length == b.length and a.rank > b.rank


class DouDizhu:
    """Authoritative state behind reset / observe / legal_actions / step / outcome."""

    def reset(self, seed, max_steps=400):
        rng = random.Random(seed)
        deck = [r for r in range(3, TWO + 1) for _ in range(8)] + [BLACK_JOKER, RED_JOKER] * 2  # R1: two decks
        rng.shuffle(deck)
        self.landlord = rng.randrange(3)  # R4
        self.kitty = sorted(deck[99:])  # R3, R5: 33 each, 9 in the kitty
        self.hands = [sorted(deck[i * 33:(i + 1) * 33]) for i in range(3)]
        self.hands[self.landlord] = sorted(self.hands[self.landlord] + self.kitty)
        self.turn = self.landlord  # R6
        self.last = None  # (seat, label, Combo) to beat; None means the turn player leads
        self.passes = 0
        self.history = []  # public (seat, label or "pass")
        self.bombs = 0
        self.steps = 0
        self.max_steps = max_steps
        self.winner = None
        self.reason = None
        return self.observe(self.turn)

    def observe(self, seat):
        """R15: only what this seat may know."""
        if seat not in range(3):  # a negative index would return another seat's hand
            raise ValueError(f"no seat {seat!r}")
        return {
            "seat": seat,
            "role": "landlord" if seat == self.landlord else "peasant",
            "landlord": self.landlord,
            "teammate": None if seat == self.landlord else 3 - seat - self.landlord,  # R19
            "hand": label(self.hands[seat]),
            "kitty": label(self.kitty),
            "cards_left": [len(h) for h in self.hands],
            "turn": self.turn,
            "to_beat": self.last and {"seat": self.last[0], "cards": self.last[1]},
            "history": [list(h) for h in self.history],
            "status": "terminal" if self.reason else "ongoing",
        }

    def _moves(self, seat):
        if self.reason or seat != self.turn:
            return {}
        moves = all_moves(self.hands[seat])
        if self.last:
            moves = {k: m for k, m in moves.items() if beats(m, self.last[2])}
        return moves

    def legal_actions(self, seat):
        moves = sorted(self._moves(seat), key=lambda k: (len(k.split()), parse(k)))
        if moves or (self.last and not self.reason and seat == self.turn):
            return moves + (["pass"] if self.last else [])  # R11
        return []

    def step(self, seat, action):
        """R16: a refused action returns ok=False and changes nothing."""
        if self.reason:
            return {"ok": False, "error": "episode is over"}
        if seat != self.turn:
            return {"ok": False, "error": f"not seat {seat}'s turn"}
        if not isinstance(action, str):
            return {"ok": False, "error": f"action must be text, got {type(action).__name__}"}
        moves = self._moves(seat)
        if action.strip().lower() == "pass":
            if not self.last:
                return {"ok": False, "error": "the leader cannot pass"}
            action = "pass"
        else:
            try:
                action = label(parse(action))
            except KeyError:
                return {"ok": False, "error": f"unknown card in {action!r}"}
            if action not in moves:
                return {"ok": False, "error": f"{action!r} is not a legal play"}

        self.steps += 1
        self.history.append((seat, action))
        if action == "pass":
            self.passes += 1
            if self.passes == 2:  # R11: the last player to play leads next
                self.last, self.passes = None, 0
        else:
            combo = moves[action]
            for card in parse(action):
                self.hands[seat].remove(card)
            self.last, self.passes = (seat, action, combo), 0
            self.bombs += combo.kind in ("bomb", "rocket")
            if not self.hands[seat]:
                self.winner, self.reason = seat, "hand_empty"  # R12
        self.turn = (seat + 1) % 3
        if not self.reason and self.steps >= self.max_steps:
            self.reason = "step_limit"  # R14
        return {"ok": True, "seat": seat, "action": action}

    def outcome(self):
        """R12, R13."""
        if not self.reason:
            return {"status": "ongoing"}
        if self.winner is None:
            return {"status": "terminal", "reason": self.reason, "winner": None,
                    "spring": False, "multiplier": 1, "scores": [0, 0, 0]}
        landlord_won = self.winner == self.landlord
        plays = Counter(s for s, a in self.history if a != "pass")
        if landlord_won:
            spring = sum(plays.values()) == plays[self.landlord]
        else:
            spring = plays[self.landlord] == 1
        multiplier = 2 ** (self.bombs + spring)
        sign = 1 if landlord_won else -1
        scores = [2 * sign * multiplier if s == self.landlord else -sign * multiplier for s in range(3)]
        return {
            "status": "terminal",
            "reason": self.reason,
            "winner": "landlord" if landlord_won else "peasants",
            "spring": spring,
            "multiplier": multiplier,
            "scores": scores,
        }
