"""The five operations: deal, turns, information, scoring, limits (README rules R1-R6, R11-R16)."""
import random
import unittest
from collections import Counter

from doudizhu.engine import DouDizhu, parse

FULL_DECK = Counter([r for r in range(3, 16) for _ in range(8)] + [16, 17] * 2)  # R1: two decks, 108 cards


def game_with(hands, landlord=0):
    g = DouDizhu()
    g.reset(0)
    g.hands = [parse(h) for h in hands]
    g.landlord = g.turn = landlord
    return g


def snapshot(g):
    return [g.observe(i) for i in range(3)], g.outcome()


class Deal(unittest.TestCase):
    """R1, R3, R4, R5."""

    def test_deal_sizes_and_kitty(self):
        for seed in range(20):
            g = DouDizhu()
            obs = g.reset(seed)
            sizes = sorted(len(h) for h in g.hands)
            self.assertEqual(sizes, [33, 33, 42])  # R3: 33 each, 9 in the kitty
            self.assertEqual(Counter(c for h in g.hands for c in h), FULL_DECK)
            self.assertFalse(Counter(g.kitty) - Counter(g.hands[g.landlord]))
            self.assertEqual(obs["kitty"], g.observe(1)["kitty"])

    def test_seed_decides(self):
        a, b = DouDizhu(), DouDizhu()
        a.reset(7)
        b.reset(7)
        self.assertEqual((a.hands, a.landlord), (b.hands, b.landlord))
        landlords = set()
        for seed in range(10):
            a.reset(seed)
            landlords.add(a.landlord)
        self.assertGreater(len(landlords), 1)


class Turns(unittest.TestCase):
    """R6, R11, R16."""

    def test_landlord_leads_and_cannot_pass(self):
        g = DouDizhu()
        g.reset(3)
        self.assertEqual(g.turn, g.landlord)
        self.assertNotIn("pass", g.legal_actions(g.landlord))
        self.assertFalse(g.step(g.landlord, "pass")["ok"])

    def test_refused_actions_change_nothing(self):
        g = DouDizhu()
        g.reset(3)
        other = (g.landlord + 1) % 3
        before = snapshot(g)
        self.assertEqual(g.legal_actions(other), [])
        for seat, action in [(other, g.legal_actions(g.landlord)[0]),
                             (g.landlord, "garbage"),
                             (g.landlord, "3 5"),
                             (g.landlord, "BJ RJ")]:  # never a play with two decks (R10a)
            self.assertFalse(g.step(seat, action)["ok"], action)
        self.assertEqual(snapshot(g), before)

    def test_card_order_does_not_matter(self):
        g = game_with(["3 3 3 4 9", "5", "6"])
        self.assertTrue(g.step(0, "4 3 3 3")["ok"])
        self.assertEqual(g.observe(0)["hand"], "9")

    def test_two_passes_return_the_lead(self):
        g = game_with(["3 9", "4 4", "5 5"])
        g.step(0, "9")
        self.assertEqual(g.legal_actions(1), ["pass"])
        g.step(1, "pass")
        g.step(2, "pass")
        self.assertEqual(g.turn, 0)
        self.assertIsNone(g.observe(0)["to_beat"])
        self.assertEqual(g.legal_actions(0), ["3"])

    def test_full_games_end_and_conserve_cards(self):
        for seed in range(50):
            g = DouDizhu()
            g.reset(seed)
            while g.outcome()["status"] == "ongoing":
                self.assertTrue(g.step(g.turn, g.legal_actions(g.turn)[0])["ok"])
                played = sum(len(a.split()) for _, a in g.history if a != "pass")
                self.assertEqual(sum(len(h) for h in g.hands) + played, 108)
            out = g.outcome()
            self.assertEqual(out["reason"], "hand_empty")
            self.assertEqual(sum(out["scores"]), 0)


class TwoDeckBombs(unittest.TestCase):
    """R10a through legal_actions and step, and the heuristic's bomb choice."""

    def test_shorter_bomb_cannot_beat_a_longer_one(self):
        g = game_with(["3 3 3 3 3 4", "9 9 9 9 K", "BJ RJ 6"], landlord=0)
        self.assertTrue(g.step(0, "3 3 3 3 3")["ok"])
        self.assertNotIn("9 9 9 9", g.legal_actions(1))
        before = snapshot(g)
        self.assertFalse(g.step(1, "9 9 9 9")["ok"])
        self.assertEqual(snapshot(g), before)

    def test_one_of_each_joker_is_refused(self):
        g = game_with(["BJ RJ 6", "5", "7"], landlord=0)
        self.assertNotIn("BJ RJ", g.legal_actions(0))
        before = snapshot(g)
        self.assertFalse(g.step(0, "BJ RJ")["ok"])
        self.assertEqual(snapshot(g), before)

    def test_heuristic_spends_its_smallest_bomb(self):
        from players import heuristic
        g = game_with(["K Q", "J", "3 3 3 3 3 9 9 9 9 4"], landlord=0)
        self.assertTrue(g.step(0, "K")["ok"])
        self.assertTrue(g.step(1, "pass")["ok"])
        self.assertEqual(heuristic.choose(g.observe(2), g.legal_actions(2)), "3 3 3 3")  # not the 5-card 3s or the 9s


class Information(unittest.TestCase):
    """R15: what a seat sees does not depend on how the other hands are split."""

    def test_reshuffling_other_hands_is_invisible(self):
        for seed in range(10):
            g = DouDizhu()
            g.reset(seed)
            g.step(g.turn, g.legal_actions(g.turn)[0])
            for viewer in range(3):
                others = [s for s in range(3) if s != viewer]
                before = g.observe(viewer), g.legal_actions(viewer)
                saved = [list(h) for h in g.hands]
                pool = g.hands[others[0]] + g.hands[others[1]]
                random.Random(seed).shuffle(pool)
                cut = len(g.hands[others[0]])
                g.hands[others[0]], g.hands[others[1]] = sorted(pool[:cut]), sorted(pool[cut:])
                self.assertEqual((g.observe(viewer), g.legal_actions(viewer)), before)
                g.hands = saved

    def test_teammate_is_named(self):
        """R19: a peasant sees the other peasant's seat; the landlord has no teammate."""
        for seed in range(6):
            g = DouDizhu()
            g.reset(seed)
            peasants = [s for s in range(3) if s != g.landlord]
            self.assertIsNone(g.observe(g.landlord)["teammate"])
            self.assertEqual(g.observe(peasants[0])["teammate"], peasants[1])
            self.assertEqual(g.observe(peasants[1])["teammate"], peasants[0])


class Scoring(unittest.TestCase):
    """R12, R13."""

    def play(self, g, moves):
        for seat, action in moves:
            self.assertTrue(g.step(seat, action)["ok"], action)
        return g.outcome()

    def test_landlord_spring(self):
        out = self.play(game_with(["3 3 3 4", "5", "6"]), [(0, "3 3 3 4")])
        self.assertEqual((out["winner"], out["spring"], out["scores"]), ("landlord", True, [4, -2, -2]))

    def test_bomb_doubles(self):
        g = game_with(["5 5 5 5 6", "7", "8"])
        out = self.play(g, [(0, "5 5 5 5"), (1, "pass"), (2, "pass"), (0, "6")])
        self.assertEqual((out["multiplier"], out["scores"]), (4, [8, -4, -4]))

    def test_peasant_anti_spring(self):
        out = self.play(game_with(["3 4", "5", "6"]), [(0, "3"), (1, "5")])
        self.assertEqual((out["winner"], out["spring"], out["scores"]), ("peasants", True, [-4, 2, 2]))

    def test_peasants_win_plain(self):
        g = game_with(["3 4 9", "5 A", "6 7"])
        out = self.play(g, [(0, "3"), (1, "5"), (2, "6"), (0, "9"), (1, "A")])
        self.assertEqual((out["spring"], out["scores"]), (False, [-2, 1, 1]))

    # Regression guards from the 2026-10-28 rules review (finding 14); they pass on the current engine.
    def test_landlord_wins_without_spring(self):
        out = self.play(game_with(["3 9", "5 6", "4 7"]), [(0, "3"), (1, "5"), (2, "7"), (0, "9")])
        self.assertEqual((out["winner"], out["spring"], out["scores"]), ("landlord", False, [2, -1, -1]))

    def test_rocket_doubles(self):
        g = game_with(["3 9 BJ BJ RJ RJ", "4 A", "5 K"])
        out = self.play(g, [(0, "3"), (1, "4"), (2, "5"), (0, "BJ BJ RJ RJ"), (1, "pass"), (2, "pass"), (0, "9")])
        self.assertEqual((out["multiplier"], out["scores"]), (2, [4, -2, -2]))

    def test_two_bombs_multiply(self):
        g = game_with(["3 5 5 5 5 9", "4 6 6 6 6", "7 K"])
        out = self.play(g, [(0, "3"), (1, "4"), (2, "7"), (0, "5 5 5 5"), (1, "6 6 6 6")])
        self.assertEqual((out["winner"], out["multiplier"], out["scores"]), ("peasants", 4, [-8, 4, 4]))


class Limits(unittest.TestCase):
    """R14."""

    def test_default_step_limit_covers_a_two_deck_deal(self):
        g = DouDizhu()
        g.reset(0)
        self.assertEqual(g.max_steps, 400)  # natural bound: 106 plays + 2 passes between = 316

    def test_step_limit_ends_the_episode(self):
        g = DouDizhu()
        g.reset(0, max_steps=3)
        for _ in range(3):
            g.step(g.turn, g.legal_actions(g.turn)[0])
        out = g.outcome()
        self.assertEqual((out["reason"], out["winner"], out["scores"]), ("step_limit", None, [0, 0, 0]))
        self.assertEqual((out["spring"], out["multiplier"]), (False, 1))  # same keys as hand_empty
        self.assertEqual(g.legal_actions(g.turn), [])
        self.assertFalse(g.step(g.turn, "3")["ok"])


if __name__ == "__main__":
    unittest.main()
