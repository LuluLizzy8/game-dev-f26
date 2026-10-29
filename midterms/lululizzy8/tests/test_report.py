"""report.py counts: forfeits apart from losses, pairing, fallback-free stats, live/fixture grouping."""
import unittest

from report import summarize, table


def ep(player, seed, score, reason="hand_empty", winner="landlord", fallback=False, live=False,
       commit="abc", trial=0, situation="S1"):
    header = {"player": player, "seed": seed, "situation": situation, "opponents": "heuristic", "trial": trial,
              "agent_seat": 0, "live": live, "model_requested": "m" if player.startswith("model") else None,
              "game_commit": commit, "config_hash": "cfg"}
    steps = [{"type": "step", "seat": 0, "source": "fallback" if fallback else "model",
              "attempts": [{"latency": 1.0, "api_error": False, "input_tokens": 10, "output_tokens": 2}]}]
    result = {"reason": reason, "winner": winner, "agent_score": score, "invalid": 0, "calls": 1,
              "models_returned": ["m-001"] if live else []}
    return {"header": header, "steps": steps, "result": result}


class Report(unittest.TestCase):
    def setUp(self):
        self.base = [ep("heuristic", s, sc) for s, sc in [(1, 2), (2, -2), (3, 2)]]
        self.model = [ep("model-history", 1, 2), ep("model-history", 2, 2, fallback=True),
                      ep("model-history", 3, -2, reason="call_limit", winner="peasants")]
        self.baseline = {(e["header"]["seed"], "S1", "heuristic", "abc", "cfg"): e for e in self.base}

    def test_forfeits_are_not_losses(self):
        row = summarize(self.model, self.baseline)
        self.assertEqual((row["wins"], row["losses_in_play"], row["call_limit"]), (2, 0, 1))

    def test_fallback_free_stats(self):
        row = summarize(self.model, self.baseline)
        self.assertEqual(row["fallback_free_wins"], "1/2")
        self.assertEqual(row["fallback_free_mean_score"], 0.0)  # (2 + -2) / 2
        self.assertEqual(row["fallbacks"], 1)

    def test_pairing(self):
        row = summarize(self.model, self.baseline)
        # diffs: 2-2=0, 2-(-2)=4, -2-2=-4 ; results differ on seeds 2 and 3
        self.assertEqual((row["pairs"], row["paired_diff_vs_heuristic"], row["discordant_pairs"]), ("3/3", 0, "2/3"))

    def test_pairs_need_the_same_commit(self):
        other = [ep("model-history", 1, 2, commit="zzz")]
        self.assertEqual(summarize(other, self.baseline)["pairs"], "0/1")

    def test_live_and_fixture_are_separate_rows(self):
        text = table(self.base + self.model + [ep("model-history", 1, 2, live=True)])
        self.assertIn("| model-history | fixture |", text)
        self.assertIn("| model-history | live |", text)
        self.assertIn("m-001", text)

    def test_cost_column(self):
        text = table(self.model, price_in=0.30, price_out=2.50)
        # 3 episodes x (10 in, 2 out) = 30 in, 6 out -> (30*0.30 + 6*2.50) / 1e6
        self.assertIn("| 2.4e-05 |", text)


if __name__ == "__main__":
    unittest.main()
