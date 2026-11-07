"""The live "Watch the AI" server (web/serve.py), run with the scripted fixture: no network, no credentials."""
import json
import os
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from functools import partial
from pathlib import Path
from unittest import mock

from players.model import FixtureModel
from runner import load_config, run_episode
from web import serve


def finish(game, timeout=30):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        state = game.poll(0)
        if state["done"]:
            return state
        time.sleep(0.02)
    raise AssertionError("game did not finish")


class WatchGame(unittest.TestCase):
    def test_same_game_as_the_runner_and_only_the_agent_view(self):
        config, config_hash = load_config()
        with tempfile.TemporaryDirectory() as tmp:
            game = serve.Watch(5, "S2", "model-history", FixtureModel(), config, config_hash, tmp)
            state = finish(game)
            traces = list(Path(tmp).glob("*.jsonl"))
        self.assertIsNone(state["error"])
        _, steps, result = run_episode(5, "S2", "model-history", model=FixtureModel(), config=config)
        self.assertEqual(state["result"]["scores"], result["scores"])
        self.assertEqual([f["action"] for f in state["frames"]], [s["action"] for s in steps])
        self.assertEqual([f["source"] for f in state["frames"]], [s["source"] for s in steps])
        for frame in state["frames"]:
            self.assertEqual(frame["obs"]["seat"], game.agent)  # never another seat's hand
            self.assertNotIn("hands", frame["obs"])
        self.assertEqual(len(traces), 1)  # the same trace file the evaluation writes

    def test_stop_cancels_without_a_trace(self):
        config, config_hash = load_config()
        with tempfile.TemporaryDirectory() as tmp:
            game = serve.Watch(5, "S1", "model-history", FixtureModel(), config, config_hash, tmp)
            game.stopped = True
            state = finish(game)
            self.assertIn(state["error"], ("stopped", None))  # it may finish before the flag is seen

    def test_model_reason_is_one_short_line(self):
        record = {"source": "model", "attempts": [{"raw": json.dumps({"action": "3", "reason": "a\nb " + "x" * 500})}]}
        reason = serve.model_reason(record)
        self.assertNotIn("\n", reason)
        self.assertLessEqual(len(reason), serve.REASON_LIMIT)
        self.assertIsNone(serve.model_reason({"source": "heuristic"}))
        self.assertIsNone(serve.model_reason({"source": "model", "attempts": [{"raw": "not json"}]}))


class LiveStart(unittest.TestCase):
    def test_bad_requests_are_refused(self):
        live = serve.Live(tempfile.gettempdir())
        for body in ({"seed": "1", "situation": "S1", "player": "model-history"},
                     {"seed": 1, "situation": "S9", "player": "model-history"},
                     {"seed": 1, "situation": "S1", "player": "heuristic"}):
            self.assertEqual(live.start(body)[0], 400)

    def test_missing_settings_never_fall_back_to_the_fixture(self):
        live = serve.Live(tempfile.gettempdir())
        with mock.patch.dict(os.environ, {"COURSE_PROVIDER": "", "COURSE_MODEL": ""}):
            code, data = live.start({"seed": 1, "situation": "S1", "player": "model-history"})
            self.assertFalse(live.status()["live_ready"])
        self.assertEqual(code, 503)
        self.assertIn("COURSE_PROVIDER", data["error"])
        self.assertIsNone(live.model)


class FillSettings(unittest.TestCase):
    NAMES = ("COURSE_PROVIDER", "COURSE_MODEL", "GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION")

    def test_fills_missing_from_config_and_gcloud_but_keeps_what_is_set(self):
        config, _ = load_config()
        empty = {n: "" for n in self.NAMES}
        done = mock.Mock(stdout="example-project\n")
        with mock.patch.dict(os.environ, dict(empty, COURSE_MODEL="my-model")), \
                mock.patch("subprocess.run", return_value=done):
            filled = serve.fill_settings(config, gcloud="gcloud")
            self.assertEqual(os.environ["COURSE_MODEL"], "my-model")  # set by the user: kept
            self.assertEqual(os.environ["COURSE_PROVIDER"], config["model_choice"]["provider"])
            self.assertEqual(os.environ["GOOGLE_CLOUD_PROJECT"], "example-project")
        self.assertNotIn("COURSE_MODEL", filled)

    def test_no_gcloud_project_leaves_it_missing(self):
        config, _ = load_config()
        with mock.patch.dict(os.environ, {n: "" for n in self.NAMES}), \
                mock.patch("subprocess.run", return_value=mock.Mock(stdout="(unset)\n")):
            serve.fill_settings(config, gcloud="gcloud")
            self.assertFalse(serve.Live(tempfile.gettempdir()).status()["live_ready"])


class Http(unittest.TestCase):
    def setUp(self):
        serve.Handler.live = serve.Live(tempfile.gettempdir())
        quiet = mock.patch.object(serve.Handler, "log_message", lambda *a: None)
        quiet.start()
        self.addCleanup(quiet.stop)
        self.server = serve.ThreadingHTTPServer(("127.0.0.1", 0), partial(serve.Handler, directory=str(serve.HERE)))
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def test_page_status_and_bad_body(self):
        with urllib.request.urlopen(self.base + "/web/") as r:
            self.assertIn(b"Dou Dizhu", r.read())
        with urllib.request.urlopen(self.base + "/api/status") as r:
            self.assertIn("live_ready", json.loads(r.read()))
        request = urllib.request.Request(self.base + "/api/watch", data=b"[1]", method="POST")
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(request)
        self.assertEqual(caught.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
