"""Runner limits, forced/fallback labeling, prompt boundary and baselines (README R18, R20-R22; DESIGN §5, §7).

No provider SDK and no network: the model is players.model.FixtureModel.
"""
import json
import random
import tempfile
import unittest
from pathlib import Path

from doudizhu.engine import DouDizhu
from players import heuristic
from players.model import FixtureModel, build_prompt
from players.random_player import RandomPlayer
from runner import load_config, run_episode

CONFIG, _ = load_config()
BAD = "not json"


def config(**limits):
    c = json.loads(json.dumps(CONFIG))
    c["limits"].update(limits)
    return c


def agent_steps(steps, header):
    return [s for s in steps if s["seat"] == header["agent_seat"]]


class Limits(unittest.TestCase):
    """R18: forfeits with explicit reasons; failed calls count toward the budget."""

    def test_call_limit(self):
        header, steps, result = run_episode(0, "S1", "model-history", model=FixtureModel(), config=config(call_limit=3))
        self.assertEqual((result["reason"], result["forfeit"], result["calls"]), ("call_limit", True, 3))
        self.assertEqual(result["winner"], "peasants")  # S1: the agent is the landlord
        self.assertEqual(result["engine_outcome"]["status"], "ongoing")
        self.assertEqual(sum(result["scores"]), 0)
        self.assertLess(result["agent_score"], 0)

    def test_api_errors_count_as_calls_not_invalid_replies(self):
        model = FixtureModel([RuntimeError("quota")] * 5)
        header, steps, result = run_episode(0, "S1", "model-history", model=model, config=config(call_limit=4))
        self.assertEqual((result["reason"], result["calls"], result["invalid"]), ("call_limit", 4, 0))

    def test_invalid_limit(self):
        header, steps, result = run_episode(0, "S1", "model-history", model=FixtureModel([BAD] * 50),
                                            config=config(invalid_limit=3))
        self.assertEqual((result["reason"], result["invalid"]), ("invalid_limit", 3))

    def test_wall_clock_timeout(self):
        ticks = iter(range(0, 10_000, 100))  # each clock read advances 100 s
        header, steps, result = run_episode(0, "S1", "model-history", model=FixtureModel(),
                                            config=config(wall_clock_seconds=250), clock=lambda: next(ticks))
        self.assertEqual(result["reason"], "timeout")

    def test_peasant_forfeit_loses_for_both_peasants(self):
        header, steps, result = run_episode(0, "S2", "model-history", model=FixtureModel(), config=config(call_limit=1))
        landlord = header["landlord"]
        self.assertEqual(result["winner"], "landlord")
        self.assertTrue(all(result["scores"][s] < 0 for s in range(3) if s != landlord))

    def test_step_limit_has_no_winner(self):
        header, steps, result = run_episode(0, "S1", "heuristic", config=config(max_steps=5))
        self.assertEqual((result["reason"], result["winner"], result["agent_score"]), ("step_limit", None, 0))


class Fallback(unittest.TestCase):
    """R21: a failed reply plus a failed retry is played by the heuristic and labeled, never as 'model'."""

    def test_fallback_is_labeled(self):
        header, steps, result = run_episode(0, "S1", "model-history", model=FixtureModel([BAD, BAD]))
        first = [s for s in agent_steps(steps, header) if "attempts" in s][0]
        self.assertEqual(first["source"], "fallback")
        self.assertEqual(len(first["attempts"]), 2)
        self.assertEqual(result["invalid"], 2)

    def test_retry_sees_the_error(self):
        model = FixtureModel([BAD])
        run_episode(0, "S1", "model-history", model=model)
        self.assertNotIn("rejected", model.prompts[0])
        self.assertIn("Your previous reply was rejected: reply was not valid JSON", model.prompts[1])

    def test_card_order_in_reply_does_not_matter(self):
        g = DouDizhu()
        g.reset(0)
        legal = g.legal_actions(g.turn)
        play = next(a for a in legal if len(a.split()) == 5)
        shuffled = " ".join(reversed(play.split())).lower()
        reply = FixtureModel([json.dumps({"action": shuffled})]).ask("x", legal)
        self.assertEqual(reply.action, play)


class Forced(unittest.TestCase):
    """R20: single-option turns cost no call and are labeled 'forced'."""

    def test_forced_moves_make_no_call(self):
        model = FixtureModel()
        header, steps, result = run_episode(0, "S2", "model-history", model=model)
        mine = agent_steps(steps, header)
        forced = [s for s in mine if s["source"] == "forced"]
        self.assertTrue(forced)
        self.assertTrue(all("attempts" not in s for s in forced))
        self.assertEqual(result["calls"], len(model.prompts))
        self.assertEqual(result["calls"], sum(len(s.get("attempts", [])) for s in mine))


class Prompt(unittest.TestCase):
    """2c: the prompt is built only from the seat's observation and legal list (R22 for the variants)."""

    def reshuffled_prompts(self, g, viewer, variant):
        others = [s for s in range(3) if s != viewer]
        before = build_prompt(g.observe(viewer), g.legal_actions(viewer), variant)
        saved = [list(h) for h in g.hands]
        pool = g.hands[others[0]] + g.hands[others[1]]
        random.Random(viewer).shuffle(pool)
        cut = len(g.hands[others[0]])
        g.hands[others[0]], g.hands[others[1]] = sorted(pool[:cut]), sorted(pool[cut:])
        after = build_prompt(g.observe(viewer), g.legal_actions(viewer), variant)
        g.hands = saved
        return before, after

    def test_prompt_unchanged_when_hidden_hands_reshuffle(self):
        for seed in range(8):
            g = DouDizhu()
            g.reset(seed)
            for _ in range(seed % 4):  # include the very first turn (the reset() return case)
                g.step(g.turn, heuristic.choose(g.observe(g.turn), g.legal_actions(g.turn)))
            for variant in ("model-history", "model-obs"):
                before, after = self.reshuffled_prompts(g, g.turn, variant)
                self.assertEqual(before, after)

    def test_no_seed_or_trace_path_in_prompts(self):
        model = FixtureModel()
        with tempfile.TemporaryDirectory() as d:
            trace = Path(d) / "secret_trace_name.jsonl"
            run_episode(12345, "S2", "model-history", model=model, trace_path=trace)
        self.assertTrue(model.prompts)
        for p in model.prompts:
            self.assertNotIn("12345", p)
            self.assertNotIn("secret_trace_name", p)

    def test_model_obs_has_no_history(self):
        g = DouDizhu()
        g.reset(1)
        g.step(g.turn, heuristic.choose(g.observe(g.turn), g.legal_actions(g.turn)))
        obs, legal = g.observe(g.turn), g.legal_actions(g.turn)
        self.assertIn("History", build_prompt(obs, legal, "model-history"))
        no_history = build_prompt(obs, legal, "model-obs")
        self.assertNotIn("History", no_history)
        self.assertNotIn("last action", no_history)
        self.assertIn("To beat:", no_history)


class Baselines(unittest.TestCase):
    def test_baselines_finish_deals_without_illegal_moves(self):
        for seed in range(50):
            for player in ("heuristic", "random"):
                header, steps, result = run_episode(seed, "S1", player)  # run_episode asserts every step is accepted
                self.assertEqual(result["reason"], "hand_empty")

    def test_heuristic_ignores_hidden_hands(self):
        for seed in range(10):
            g = DouDizhu()
            g.reset(seed)
            g.step(g.turn, heuristic.choose(g.observe(g.turn), g.legal_actions(g.turn)))
            seat = g.turn
            before = heuristic.choose(g.observe(seat), g.legal_actions(seat))
            others = [s for s in range(3) if s != seat]
            pool = g.hands[others[0]] + g.hands[others[1]]
            random.Random(seed).shuffle(pool)
            cut = len(g.hands[others[0]])
            g.hands[others[0]], g.hands[others[1]] = sorted(pool[:cut]), sorted(pool[cut:])
            self.assertEqual(heuristic.choose(g.observe(seat), g.legal_actions(seat)), before)

    def test_random_player_is_seeded(self):
        a, b = RandomPlayer(3), RandomPlayer(3)
        self.assertEqual([a.choose({}, list("abcd")) for _ in range(5)], [b.choose({}, list("abcd")) for _ in range(5)])


class Trace(unittest.TestCase):
    def test_trace_has_header_steps_and_result(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "t.jsonl"
            run_episode(2, "S3", "model-obs", model=FixtureModel(), trace_path=path)
            lines = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual((lines[0]["type"], lines[-1]["type"]), ("header", "result"))
        self.assertFalse(lines[0]["live"])
        self.assertEqual(lines[0]["model"], "scripted-fixture-v1")
        self.assertIn(lines[-1]["reason"], ("hand_empty", "step_limit", "call_limit", "timeout", "invalid_limit"))
        sources = {l["source"] for l in lines if l["type"] == "step"}
        self.assertLessEqual(sources, {"model", "fallback", "forced", "heuristic"})


if __name__ == "__main__":
    unittest.main()
