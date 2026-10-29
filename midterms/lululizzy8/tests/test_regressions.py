"""Bugs actually found during development. Each test was committed failing before its fix."""
import unittest

from doudizhu.engine import DouDizhu
from test_game import snapshot


class FoundByRulesReview20261028(unittest.TestCase):
    """reviews/2026-10-28-design-review.md, rules reviewer findings 9 and 10."""

    def setUp(self):
        self.g = DouDizhu()
        self.g.reset(0)

    def test_observe_rejects_out_of_range_seat(self):
        # Bug: observe(-1) used Python negative indexing and returned seat 2's hand.
        for seat in (-1, 3):
            with self.assertRaises(ValueError):
                self.g.observe(seat)

    def test_step_refuses_non_string_action(self):
        # Bug: a model reply like {"action": 3} or null crashed step with AttributeError.
        before = snapshot(self.g), [list(h) for h in self.g.hands]
        for action in (3, None, ["3"]):
            result = self.g.step(self.g.turn, action)
            self.assertFalse(result["ok"])
        self.assertEqual((snapshot(self.g), [list(h) for h in self.g.hands]), before)
        self.assertEqual(self.g.steps, 0)


class FoundInFirstLiveRun20261028(unittest.TestCase):
    """First live tuning run (traces/tuning, seed 100): writing a trace made the folder look modified, so the
    next run's game_commit got "-dirty", and report.py could not pair the model with its heuristic baseline."""

    def test_outputs_do_not_mark_the_code_dirty(self):
        from runner import is_dirty
        self.assertFalse(is_dirty(["?? traces/", "?? results/tuning.md", " M traces/tuning/a.jsonl"]))
        self.assertTrue(is_dirty(["?? traces/", " M runner.py"]))
        self.assertFalse(is_dirty([]))


if __name__ == "__main__":
    unittest.main()
