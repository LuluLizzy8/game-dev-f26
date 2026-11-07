"""R10b Revolution: a bomb of 6+ cards flips the order of 3 through 2 until another 6+ bomb flips it back."""
import unittest

from doudizhu.engine import Combo, DouDizhu, beats, parse
from doudizhu.view import render
from players import heuristic


def game_with(hands, landlord=0):
    g = DouDizhu()
    g.reset(0)
    g.hands = [parse(h) for h in hands]
    g.landlord = g.turn = landlord
    return g


class Beats(unittest.TestCase):
    def test_low_ranks_win_in_a_revolution(self):
        self.assertTrue(beats(Combo("single", 3, 1), Combo("single", 15, 1), revolution=True))
        self.assertFalse(beats(Combo("single", 15, 1), Combo("single", 3, 1), revolution=True))
        self.assertTrue(beats(Combo("straight", 3, 5), Combo("straight", 4, 5), revolution=True))
        self.assertFalse(beats(Combo("single", 3, 1), Combo("single", 15, 1)))  # normal order unchanged

    def test_jokers_stay_on_top(self):
        self.assertTrue(beats(Combo("single", 16, 1), Combo("single", 3, 1), revolution=True))
        self.assertFalse(beats(Combo("single", 3, 1), Combo("single", 16, 1), revolution=True))
        self.assertTrue(beats(Combo("pair", 16, 1), Combo("pair", 3, 1), revolution=True))

    def test_every_ranked_kind_flips(self):
        for kind, length in (("pair_seq", 3), ("plane", 2), ("plane+1", 2), ("plane+2", 2),
                             ("triple+1", 1), ("triple+2", 1), ("four+2", 1), ("four+2pairs", 1)):
            self.assertTrue(beats(Combo(kind, 3, length), Combo(kind, 9, length), revolution=True), kind)
            self.assertFalse(beats(Combo(kind, 3, length), Combo(kind, 9, length)), kind)

    def test_bombs_compare_by_size_then_flipped_rank(self):
        self.assertTrue(beats(Combo("bomb", 3, 4), Combo("bomb", 13, 4), revolution=True))
        self.assertTrue(beats(Combo("bomb", 13, 5), Combo("bomb", 3, 4), revolution=True))
        self.assertFalse(beats(Combo("bomb", 3, 4), Combo("bomb", 13, 5), revolution=True))


class Engine(unittest.TestCase):
    def test_six_card_bomb_starts_and_ends_a_revolution(self):
        g = game_with(["3 3 3 3 3 3 4", "K K K K K K K 5", "Q 6"])
        self.assertEqual([g.observe(s)["revolution"] for s in range(3)], [False] * 3)  # R15: public, starts off
        g.step(0, "3 3 3 3 3 3")
        self.assertEqual([g.observe(s)["revolution"] for s in range(3)], [True] * 3)
        g.step(1, "K K K K K K K")  # a longer bomb beats it, and as a 6+ bomb it flips the order back
        self.assertFalse(g.observe(0)["revolution"])
        self.assertEqual(g.bombs, 2)  # each still doubles the stakes (R13)

    def test_five_card_bomb_does_not_flip(self):
        g = game_with(["3 3 3 3 3 4", "5", "6"])
        g.step(0, "3 3 3 3 3")
        self.assertFalse(g.observe(0)["revolution"])

    def test_followers_need_a_lower_rank_in_a_revolution(self):
        g = game_with(["3 3 3 3 3 3 9 4", "5 2", "K Q"])
        g.step(0, "3 3 3 3 3 3")
        g.step(1, "pass")
        g.step(2, "pass")
        g.step(0, "9")
        self.assertEqual(g.legal_actions(1), ["5", "pass"])
        self.assertFalse(g.step(1, "2")["ok"])
        self.assertTrue(g.observe(1)["revolution"])  # the refused move changed nothing

    def test_refused_bomb_does_not_flip(self):
        g = game_with(["3 3 3 3 3 3 4", "5", "6"])
        g.step(0, "3 3 3 3 3 3 3")  # seven 3s: not held
        self.assertFalse(g.observe(0)["revolution"])


class Heuristic(unittest.TestCase):
    def test_starts_a_revolution_with_a_low_hand(self):
        g = game_with(["3 3 3 3 3 3 4 5 6 7 K", "Q", "J"])
        self.assertEqual(heuristic.choose(g.observe(0), g.legal_actions(0)), "3 3 3 3 3 3")

    def test_never_flips_over_its_teammate(self):
        g = game_with(["Q 8", "5 5 5", "3 3 3 3 3 3 4 5 6 7 K"], landlord=0)
        g.step(0, "Q")
        g.step(1, "5")  # seat 1 is seat 2's teammate
        self.assertEqual(heuristic.choose(g.observe(2), g.legal_actions(2)), "pass")

    def test_keeps_the_order_with_a_high_hand(self):  # regression guard: passed before R10b too
        g = game_with(["3 3 3 3 3 3 K K A A 2 2 Q", "Q", "J"])
        self.assertNotEqual(heuristic.choose(g.observe(0), g.legal_actions(0)), "3 3 3 3 3 3")

    def test_leads_its_weakest_card_in_a_revolution(self):
        g = game_with(["3 3 3 3 3 3 4 2 9 5 6 7", "Q", "J"])
        g.step(0, "3 3 3 3 3 3")
        g.step(1, "pass")
        g.step(2, "pass")
        self.assertEqual(heuristic.choose(g.observe(0), g.legal_actions(0)), "2")  # 2 is now the lowest rank


class View(unittest.TestCase):
    def test_table_text_says_when_the_order_is_flipped(self):
        g = game_with(["3 3 3 3 3 3 4", "5", "6"])
        self.assertNotIn("REVOLUTION", render(g.observe(1)))
        g.step(0, "3 3 3 3 3 3")
        self.assertIn("REVOLUTION", render(g.observe(1)))


if __name__ == "__main__":
    unittest.main()
