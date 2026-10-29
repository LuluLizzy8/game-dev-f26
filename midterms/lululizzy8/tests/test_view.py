"""The table view shows the public game state and nothing hidden (README R15)."""
import random
import unittest

from doudizhu.engine import DouDizhu, parse
from doudizhu.view import render


def game_with(hands, landlord=0):
    g = DouDizhu()
    g.reset(0)
    g.hands = [parse(h) for h in hands]
    g.landlord = g.turn = landlord
    return g


class View(unittest.TestCase):
    def test_shows_turn_play_to_beat_and_last_actions(self):
        g = game_with(["3 9 K", "4 4 5", "6 6 7"])
        g.step(0, "9")
        g.step(1, "pass")
        text = render(g.observe(2))
        self.assertIn("You are seat 2 (peasant, you).", text)
        self.assertIn("Turn: seat 2 (peasant, you)", text)
        self.assertIn("To beat: 9 played by seat 0 (landlord)", text)
        self.assertIn("seat 1 (peasant, teammate): 3 cards, last action: pass", text)
        self.assertIn("Your hand: 6 6 7", text)

    def test_leader_and_terminal(self):
        g = game_with(["3 9", "4", "5"])
        self.assertIn("To beat: nothing", render(g.observe(0)))
        g.step(0, "9")
        g.step(1, "pass")
        g.step(2, "pass")
        g.step(0, "3")
        self.assertIn("The deal is over.", render(g.observe(1)))

    def test_hidden_hands_do_not_change_the_view(self):
        for seed in range(10):
            g = DouDizhu()
            g.reset(seed)
            g.step(g.turn, g.legal_actions(g.turn)[0])
            for viewer in range(3):
                others = [s for s in range(3) if s != viewer]
                before = render(g.observe(viewer))
                pool = g.hands[others[0]] + g.hands[others[1]]
                random.Random(seed).shuffle(pool)
                cut = len(g.hands[others[0]])
                saved = [list(h) for h in g.hands]
                g.hands[others[0]], g.hands[others[1]] = sorted(pool[:cut]), sorted(pool[cut:])
                self.assertEqual(render(g.observe(viewer)), before)
                g.hands = saved


if __name__ == "__main__":
    unittest.main()
