"""The browser session (web/session.py) plays the same deal as the engine and shows only your own hand."""
import json
import unittest

from doudizhu.engine import DouDizhu, all_moves
from players import heuristic
from web.session import Session, seed_with_landlord


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
        for seat in range(3):  # find a seat whose first turn has a multi-card play
            s = Session(7, seat)
            first = json.loads(s.start())
            action = next((a for a in first["legal"] if len(a.split()) > 1 and a != "pass"), None)
            if action:
                break
        reply = json.loads(s.play(" ".join(reversed(action.split())).lower()))
        self.assertTrue(reply["ok"])

    def test_watch_mode_plays_the_all_heuristic_deal(self):
        for seed in range(3):
            reply = json.loads(Session(seed, 1, watch=True).start())
            outcome, history = all_heuristic(seed)
            self.assertEqual(reply["outcome"], outcome)
            self.assertEqual(len(reply["frames"]), len(history) + 1)  # the deal, then one frame per move
            self.assertEqual(reply["frames"][0]["history"], [])
            for frame in reply["frames"]:
                self.assertEqual(frame["seat"], 1)

    def test_refusals_say_why(self):
        s = Session(7, 0)
        s.start()
        self.assertIn("not a combination", s.explain("3 4"))
        self.assertIn("not cards", s.explain("XX"))
        self.assertIsNone(s.explain(s.g.legal_actions(s.seat)[0]))
        refused = json.loads(s.play("3 4"))
        self.assertIn("not a combination", refused["error"])

    def test_following_explains_kind_and_rank(self):
        s = Session(0, 0)
        s.g.turn, s.g.last = 0, (1, "9 9", all_moves([9, 9])["9 9"])  # seat 0 must beat a pair of 9s
        self.assertIn("To follow a pair", s.explain("3"))
        self.assertIn("does not rank higher", s.explain("4 4"))

    def test_seed_with_landlord_rotates_the_landlord(self):
        seed = 100
        for landlord in (1, 2, 0, 1):
            seed = seed_with_landlord(landlord, seed + 1)
            self.assertEqual(json.loads(Session(seed, 0).start())["obs"]["landlord"], landlord)

    def test_page_sees_only_its_own_hand(self):
        s = Session(3, 1)
        reply = json.loads(s.start())
        for obs in [*reply["frames"], reply["obs"]]:
            self.assertEqual(obs["seat"], 1)
            self.assertEqual(len(obs["hand"].split()), obs["cards_left"][1])
        self.assertNotIn("hands", json.dumps(reply))


if __name__ == "__main__":
    unittest.main()
