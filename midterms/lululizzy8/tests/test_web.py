"""The browser session (web/session.py) plays the same deal as the engine and shows only your own hand."""
import json
import unittest

from doudizhu.engine import DouDizhu
from players import heuristic
from web.session import Session


def all_heuristic(seed):
    g = DouDizhu()
    g.reset(seed)
    while g.outcome()["status"] == "ongoing":
        s = g.turn
        g.step(s, heuristic.choose(g.observe(s), g.legal_actions(s)))
    return g.outcome(), g.history


class WebSession(unittest.TestCase):
    def test_hint_moves_reproduce_the_all_heuristic_deal(self):
        for seed in range(5):
            for seat in range(3):
                s = Session(seed, seat)
                reply = json.loads(s.start())
                while reply["outcome"]["status"] == "ongoing":
                    reply = json.loads(s.play(s.hint()))
                    self.assertTrue(reply["ok"])
                outcome, history = all_heuristic(seed)
                self.assertEqual(reply["outcome"], outcome)
                self.assertEqual([tuple(h) for h in reply["obs"]["history"]], history)

    def test_refused_move_changes_nothing(self):
        s = Session(7, 0)
        before = json.loads(s.start())
        reply = json.loads(s.play("3 4"))  # never a combination
        self.assertFalse(reply["ok"])
        self.assertEqual(reply["frames"], [])
        self.assertEqual(reply["obs"], before["obs"])
        reply = json.loads(s.play("XX"))
        self.assertFalse(reply["ok"])

    def test_card_order_and_case_do_not_matter(self):
        s = Session(7, 0)
        first = json.loads(s.start())
        action = next(a for a in first["legal"] if len(a.split()) > 1 and a != "pass")
        reply = json.loads(s.play(" ".join(reversed(action.split())).lower()))
        self.assertTrue(reply["ok"])

    def test_page_sees_only_its_own_hand(self):
        s = Session(3, 1)
        reply = json.loads(s.start())
        for obs in [*reply["frames"], reply["obs"]]:
            self.assertEqual(obs["seat"], 1)
            self.assertEqual(len(obs["hand"].split()), obs["cards_left"][1])
        self.assertNotIn("hands", json.dumps(reply))


if __name__ == "__main__":
    unittest.main()
