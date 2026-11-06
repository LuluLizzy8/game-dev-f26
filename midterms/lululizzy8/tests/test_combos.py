"""Card combinations and what beats what (README rules R2, R7-R10)."""
import random
import unittest
from collections import Counter

from doudizhu.engine import Combo, all_moves, beats, label, parse


def kind_of(hand, play):
    move = all_moves(parse(hand)).get(label(parse(play)))
    return move and move.kind


class Lead(unittest.TestCase):
    """R7: each combination can be led from a hand that holds exactly it."""

    CASES = [
        ("3", "single"),
        ("3 3", "pair"),
        ("3 3 3", "triple"),
        ("3 3 3 9", "triple+1"),
        ("3 3 3 9 9", "triple+2"),
        ("3 4 5 6 7", "straight"),
        ("10 J Q K A", "straight"),
        ("3 3 4 4 5 5", "pair_seq"),
        ("3 3 3 4 4 4", "plane"),
        ("3 3 3 4 4 4 8 9", "plane+1"),
        ("3 3 3 4 4 4 8 8 9 9", "plane+2"),
        ("3 3 3 3 8 9", "four+2"),
        ("3 3 3 3 8 8 9 9", "four+2pairs"),
        ("3 3 3 3", "bomb"),
        ("3 3 3 3 3", "bomb"),                  # R10a: two decks, bombs of 4-8
        ("2 2 2 2 2 2 2 2", "bomb"),
        ("BJ BJ", "pair"),                      # R7: two of each joker
        ("RJ RJ", "pair"),
        ("BJ BJ RJ RJ", "rocket"),               # R10a: the rocket is all four jokers
    ]

    def test_each_kind(self):
        for hand, kind in self.CASES:
            with self.subTest(hand=hand):
                self.assertEqual(kind_of(hand, hand), kind)


class Rejected(unittest.TestCase):
    """R7, R8: shapes that are not combinations."""

    CASES = [
        ("3 4 5 6", "3 4 5 6"),                  # straight shorter than 5
        ("10 J Q K A 2", "J Q K A 2"),           # 2 cannot be in a sequence
        ("K K A A 2 2", "K K A A 2 2"),          # pair sequence through 2
        ("A A A 2 2 2", "A A A 2 2 2"),          # plane through 2
        ("3 3 4 4", "3 3 4 4"),                  # two pairs is not a pair sequence
        ("3 3 3 4 4 4 5 5", "3 3 3 4 4 4 5 5"),  # R8: plane kickers must be distinct
        ("3 3 3 4 4 4 4 5", "3 3 3 4 4 4 4 5"),  # R8: kicker shares a triple's rank
        ("3 3 3 3 5 5", "3 3 3 3 5 5"),          # R8: four + two singles of one rank
        ("3 5", "3 5"),
        ("BJ RJ", "BJ RJ"),                      # R10a: one of each joker is not a rocket
        ("BJ BJ RJ", "BJ BJ RJ"),
        ("3 3 3 3 3 8 9", "3 3 3 3 3 8"),        # five of a rank takes no kicker
    ]

    def test_not_combinations(self):
        for hand, play in self.CASES:
            with self.subTest(play=play):
                self.assertIsNone(kind_of(hand, play))

    def test_bomb_length_is_its_card_count(self):
        moves = all_moves(parse("3 3 3 3 3 3 3"))
        self.assertEqual([moves[" ".join(["3"] * n)].length for n in (4, 5, 6, 7)], [4, 5, 6, 7])


class Beats(unittest.TestCase):
    """R2, R9, R10."""

    def test_same_kind_and_length_higher_rank(self):
        self.assertTrue(beats(Combo("straight", 4, 5), Combo("straight", 3, 5)))
        self.assertFalse(beats(Combo("straight", 4, 6), Combo("straight", 3, 5)))
        self.assertFalse(beats(Combo("pair", 9, 1), Combo("single", 3, 1)))
        self.assertFalse(beats(Combo("single", 3, 1), Combo("single", 3, 1)))

    def test_rank_order_puts_two_and_jokers_on_top(self):
        order = [all_moves(parse(c))[c] for c in "A 2 BJ RJ".split()]
        for low, high in zip(order, order[1:]):
            self.assertTrue(beats(high, low))
            self.assertFalse(beats(low, high))

    def test_kicker_does_not_set_rank(self):
        moves = all_moves(parse("3 3 3 4 4 4 A"))
        self.assertTrue(beats(moves["3 4 4 4"], moves["3 3 3 A"]))
        self.assertFalse(beats(moves["3 3 3 A"], moves["3 4 4 4"]))

    def test_bombs_and_rocket(self):
        """R10a: a longer bomb beats a shorter one; same length, higher rank; the rocket beats all."""
        bomb4, bomb5, rocket = Combo("bomb", 4, 4), Combo("bomb", 5, 4), Combo("rocket", 16, 4)
        self.assertTrue(beats(bomb4, Combo("straight", 10, 5)))
        self.assertTrue(beats(bomb4, Combo("single", 17, 1)))
        self.assertTrue(beats(bomb5, bomb4))
        self.assertFalse(beats(bomb4, bomb5))
        self.assertTrue(beats(Combo("bomb", 3, 5), Combo("bomb", 15, 4)))  # five 3s beat four 2s
        self.assertFalse(beats(Combo("bomb", 15, 4), Combo("bomb", 3, 5)))
        self.assertTrue(beats(Combo("bomb", 3, 8), Combo("bomb", 15, 7)))
        self.assertTrue(beats(rocket, Combo("bomb", 15, 8)))
        self.assertFalse(beats(Combo("bomb", 15, 8), rocket))


class Invariants(unittest.TestCase):
    """R8: on random hands every move string names one combination drawn from the hand."""

    def test_random_hands(self):
        deck = [r for r in range(3, 16) for _ in range(8)] + [16, 17] * 2  # R1: two decks
        for seed in range(200):
            hand = random.Random(seed).sample(deck, (33, 42)[seed % 2])
            have = Counter(hand)
            for move in all_moves(hand):  # all_moves asserts no label maps to two combos
                self.assertFalse(Counter(parse(move)) - have, move)

    def test_rocket_spent_as_kickers_has_one_reading(self):
        moves = all_moves(parse("3 3 3 3 3 3 BJ BJ RJ RJ 5 5"))  # setdefault in all_moves asserts uniqueness
        self.assertEqual(moves["3 3 3 3 BJ BJ RJ RJ"].kind, "four+2pairs")
        self.assertEqual(moves["BJ BJ RJ RJ"].kind, "rocket")


if __name__ == "__main__":
    unittest.main()
