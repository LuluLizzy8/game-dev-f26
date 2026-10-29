"""The five operations: deal, turns, information, scoring, limits (README rules R1-R6, R11-R16)."""
import random
import unittest
from collections import Counter

from doudizhu.engine import DouDizhu, parse

FULL_DECK = Counter([r for r in range(3, 16) for _ in range(4)] + [16, 17])


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
            self.assertEqual(sizes, [17, 17, 20])
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
                             (g.landlord, "BJ BJ")]:
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
                self.assertEqual(sum(len(h) for h in g.hands) + played, 54)
            out = g.outcome()
            self.assertEqual(out["reason"], "hand_empty")
            self.assertEqual(sum(out["scores"]), 0)


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


class Limits(unittest.TestCase):
    """R14."""

    def test_step_limit_ends_the_episode(self):
        g = DouDizhu()
        g.reset(0, max_steps=3)
        for _ in range(3):
            g.step(g.turn, g.legal_actions(g.turn)[0])
        out = g.outcome()
        self.assertEqual((out["reason"], out["winner"], out["scores"]), ("step_limit", None, [0, 0, 0]))
        self.assertEqual(g.legal_actions(g.turn), [])
        self.assertFalse(g.step(g.turn, "3")["ok"])


if __name__ == "__main__":
    unittest.main()
