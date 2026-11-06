"""Local server for the browser game: serves this folder and runs live "Watch the AI" games.

    python web/serve.py              then open http://localhost:8000/web/

Play, the handbook and "Watch the baseline" run in the browser and need no server beyond static files.
"Watch the AI" calls the model live through runner.run_episode: the same limits, retries, labeled
fallbacks and trace files as the evaluation (traces/watch/). It needs the environment variables in the
README and spends cloud credits; there is no fixture substitution. Credentials stay in this process; the
page only ever receives observe(agent seat), the move, its source label and the model's one-line reason.
"""
import argparse
import json
import sys
import threading
import time
import uuid
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from doudizhu.engine import DouDizhu  # noqa: E402
from runner import PLAYERS, SITUATIONS, load_config, run_episode  # noqa: E402

MODEL_PLAYERS = [p for p in PLAYERS if p.startswith("model")]
REASON_LIMIT = 200


class Cancelled(Exception):
    pass


def model_reason(record):
    """The accepted reply's one-line reason, if the model gave one."""
    if record.get("source") != "model":
        return None
    try:
        reason = json.loads(record["attempts"][-1]["raw"]).get("reason")
    except (TypeError, ValueError, AttributeError, KeyError, IndexError):
        return None
    return " ".join(reason.split())[:REASON_LIMIT] if isinstance(reason, str) else None


class Watch:
    """One live game in a background thread; frames grow as moves are accepted."""

    def __init__(self, seed, situation, player, model, config, config_hash, trace_dir):
        g = DouDizhu()
        g.reset(seed, max_steps=config["limits"]["max_steps"])
        self.agent = (g.landlord + SITUATIONS[situation]) % 3  # same rule as run_episode
        self.start = g.observe(self.agent)
        self.frames, self.result, self.error, self.stopped = [], None, None, False
        self.calls = self.tokens_in = self.tokens_out = 0
        self.lock = threading.Lock()
        trace = Path(trace_dir) / f"{player}_{situation}_s{seed}_{time.strftime('%Y%m%d-%H%M%S')}.jsonl"
        args = (seed, situation, player, "heuristic", model, config, 0, trace)
        threading.Thread(target=self._run, args=(args, config_hash), daemon=True).start()

    def _on_step(self, g, record):
        if self.stopped:
            raise Cancelled
        attempts = record.get("attempts", [])
        frame = {"obs": g.observe(self.agent), "seat": record["seat"], "action": record["action"],
                 "source": record["source"], "reason": model_reason(record),
                 "failed_attempts": sum(a["error"] is not None for a in attempts)}
        with self.lock:
            self.calls += len(attempts)
            self.tokens_in += sum(a["input_tokens"] or 0 for a in attempts)
            self.tokens_out += sum(a["output_tokens"] or 0 for a in attempts)
            self.frames.append(frame)

    def _run(self, args, config_hash):
        try:
            _, _, result = run_episode(*args, config_hash=config_hash, on_step=self._on_step)
            self.result = {k: result[k] for k in ("status", "reason", "winner", "spring", "multiplier",
                                                   "scores", "forfeit", "calls", "invalid", "models_returned")}
        except Cancelled:
            self.error = "stopped"
        except Exception as error:  # report the type only: provider messages can contain the project ID
            self.error = f"the game stopped: {type(error).__name__}"

    def poll(self, since):
        with self.lock:
            return {"frames": self.frames[since:], "done": self.result is not None or self.error is not None,
                    "result": self.result, "error": self.error, "agent": self.agent,
                    "usage": {"calls": self.calls, "input_tokens": self.tokens_in, "output_tokens": self.tokens_out}}


class Live:
    """At most one live game at a time, so a stray tab cannot run up costs."""

    def __init__(self, trace_dir):
        self.config, self.config_hash = load_config()
        self.trace_dir, self.model, self.games, self.lock = trace_dir, None, {}, threading.Lock()

    def status(self):
        import os
        names = ("COURSE_PROVIDER", "COURSE_MODEL", "GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION")
        ready = all(os.environ.get(n, "").strip() for n in names)
        return {"live_ready": ready, "model": os.environ.get("COURSE_MODEL") if ready else None,
                "players": MODEL_PLAYERS, "situations": sorted(SITUATIONS)}

    def start(self, body):
        seed, situation, player = body.get("seed"), body.get("situation"), body.get("player")
        if not (isinstance(seed, int) and 0 <= seed < 10**9) or situation not in SITUATIONS or player not in MODEL_PLAYERS:
            return 400, {"error": "seed must be a whole number; situation S1, S2 or S3; player a model player"}
        with self.lock:
            if self.model is None:
                try:
                    from players.model import VertexModel
                    self.model = VertexModel(self.config)
                except SystemExit as missing:  # missing environment variables: say so, never fall back
                    return 503, {"error": str(missing)}
                except ImportError:
                    return 503, {"error": "google-genai is not installed (pip install -r requirements.txt)"}
            for game in self.games.values():
                game.stopped = True
            game_id = uuid.uuid4().hex
            game = Watch(seed, situation, player, self.model, self.config, self.config_hash, self.trace_dir)
            self.games = {game_id: game}
        return 200, {"id": game_id, "agent": game.agent, "start": game.start, "model": self.model.model_id}

    def poll(self, game_id, since):
        game = self.games.get(game_id)
        return (200, game.poll(since)) if game else (404, {"error": "no such game"})

    def stop(self, game_id):
        game = self.games.get(game_id)
        if game:
            game.stopped = True
        return 200, {"ok": True}


class Handler(SimpleHTTPRequestHandler):
    live = None  # set in main

    def _json(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _query(self):
        from urllib.parse import parse_qs, urlsplit
        return {k: v[0] for k, v in parse_qs(urlsplit(self.path).query).items()}

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/status":
            return self._json(200, self.live.status())
        if path == "/api/watch":
            q = self._query()
            try:
                since = int(q.get("since", 0))
            except ValueError:
                since = 0
            return self._json(*self.live.poll(q.get("id", ""), max(0, since)))
        return super().do_GET()

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length > 10_000:
            return self._json(413, {"error": "request too large"})
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            return self._json(400, {"error": "body must be JSON"})
        if not isinstance(body, dict):
            return self._json(400, {"error": "body must be a JSON object"})
        path = self.path.split("?")[0]
        if path == "/api/watch":
            return self._json(*self.live.start(body))
        if path == "/api/watch/stop":
            return self._json(*self.live.stop(str(body.get("id", ""))))
        return self._json(404, {"error": "not found"})

    def log_message(self, fmt, *args):
        if "/api/watch?" not in self.path:  # polling every half second would flood the console
            super().log_message(fmt, *args)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--host", default="127.0.0.1",
                   help="127.0.0.1 (default) keeps live games to this computer; 0.0.0.0 lets a phone on your Wi-Fi in")
    args = p.parse_args(argv)
    Handler.live = Live(HERE / "traces" / "watch")
    if args.host != "127.0.0.1":
        print("Warning: anyone on this network can open the page and start live games on your credits.")
    server = ThreadingHTTPServer((args.host, args.port), partial(Handler, directory=str(HERE)))
    print(f"Open http://localhost:{args.port}/web/  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
