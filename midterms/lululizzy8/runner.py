"""Episode runner (DESIGN.md §5). Holds the only DouDizhu instance; players get observe/legal_actions output.

    python runner.py --player heuristic --situation S1 --seeds 0-9 --out traces/dev
"""
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

from doudizhu.engine import DouDizhu
from players import heuristic
from players.model import FixtureModel, build_prompt, prompt_hash
from players.random_player import RandomPlayer

HERE = Path(__file__).resolve().parent
SITUATIONS = {"S1": 0, "S2": 1, "S3": 2}  # agent seat = (landlord + k) % 3
PLAYERS = ("heuristic", "random", "model-history", "model-obs")


def load_config(path=HERE / "agent-config.json"):
    text = Path(path).read_bytes()
    return json.loads(text), hashlib.sha256(text).hexdigest()[:12]


def game_commit():
    try:
        out = subprocess.run(["git", "-C", str(HERE), "rev-parse", "--short", "HEAD"],
                             capture_output=True, text=True, timeout=5).stdout.strip()
        dirty = subprocess.run(["git", "-C", str(HERE), "status", "--porcelain", "--", "."],
                               capture_output=True, text=True, timeout=5).stdout.strip()
        return (out or "unknown") + ("-dirty" if dirty else "")
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def forfeit(g, agent_seat, reason):
    """R18: the agent's side loses at the current bomb multiplier, no spring."""
    multiplier = 2 ** g.bombs
    agent_is_landlord = agent_seat == g.landlord
    landlord_score = -2 * multiplier if agent_is_landlord else 2 * multiplier
    scores = [landlord_score if s == g.landlord else -landlord_score // 2 for s in range(3)]
    return {"status": "terminal", "reason": reason, "forfeit": True,
            "winner": "peasants" if agent_is_landlord else "landlord",
            "spring": False, "multiplier": multiplier, "scores": scores}


def run_episode(seed, situation, player, opponents="heuristic", model=None, config=None,
                trial=0, trace_path=None, clock=time.monotonic, config_hash=None):
    if config is None:
        config, config_hash = load_config()
    elif config_hash is None:  # an in-memory config (tests): hash its content
        config_hash = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:12]
    limits = config["limits"]
    g = DouDizhu()
    g.reset(seed, max_steps=limits["max_steps"])  # return value is the landlord's view: never shown to the agent
    agent = (g.landlord + SITUATIONS[situation]) % 3
    is_model = player.startswith("model")
    if is_model and model is None:
        raise ValueError("a model player needs a model (FixtureModel or VertexModel)")
    rng_player = RandomPlayer(seed * 1000 + trial)
    rng_opponent = RandomPlayer(seed * 1000 + trial + 500)

    def baseline_choice(seat, obs, legal):
        if seat == agent:
            return rng_player.choose(obs, legal) if player == "random" else heuristic.choose(obs, legal)
        return rng_opponent.choose(obs, legal) if opponents == "random" else heuristic.choose(obs, legal)

    header = {"type": "header", "seed": seed, "situation": situation, "trial": trial, "player": player,
              "opponents": opponents, "agent_seat": agent, "landlord": g.landlord,
              "live": bool(is_model and model.live), "model_requested": model.model_id if is_model else None,
              "config_hash": config_hash, "game_commit": game_commit(), "limits": limits,
              "sampling": config.get("sampling")}
    steps, calls, invalid = [], 0, 0
    started = clock()
    result = None

    while g.outcome()["status"] == "ongoing" and result is None:
        seat = g.turn
        obs, legal = g.observe(seat), g.legal_actions(seat)
        record = {"type": "step", "step": g.steps + 1, "seat": seat}
        if len(legal) == 1:
            action, source = legal[0], "forced"  # R20
        elif seat == agent and is_model:
            action, source, error, attempts = None, None, None, []
            for _ in range(1 + limits["retries_per_turn"]):
                if calls >= limits["call_limit"]:
                    result = forfeit(g, agent, "call_limit")
                    break
                if clock() - started >= limits["wall_clock_seconds"]:
                    result = forfeit(g, agent, "timeout")
                    break
                prompt = build_prompt(obs, legal, player, error)
                reply = model.ask(prompt, legal)
                calls += 1
                attempts.append({"prompt_hash": prompt_hash(prompt), "raw": reply.raw, "error": reply.error,
                                 "api_error": reply.api_error, "latency": round(reply.latency, 3),
                                 "input_tokens": reply.input_tokens, "output_tokens": reply.output_tokens,
                                 "model": reply.model})
                if reply.action is not None:
                    action, source = reply.action, "model"
                    break
                if not reply.api_error:  # a failed call is not shown to the model: it never replied
                    invalid += 1
                    if invalid >= limits["invalid_limit"]:
                        result = forfeit(g, agent, "invalid_limit")
                        break
                    error = reply.error
            record["attempts"] = attempts
            if result is not None:
                record["forfeit"] = result["reason"]
                steps.append(record)
                break
            if action is None:
                action, source = heuristic.choose(obs, legal), "fallback"  # R21
        else:
            action = baseline_choice(seat, obs, legal)
            source = player if seat == agent else opponents
        outcome = g.step(seat, action)
        if not outcome["ok"]:  # every source picks from the legal list; a refusal here is a runner bug
            raise RuntimeError(f"refused {action!r} from {source}: {outcome}")
        record.update(action=action, source=source, accepted=True)
        steps.append(record)

    if result is None:
        result = dict(g.outcome(), forfeit=False)
    returned = sorted({a["model"] for s in steps for a in s.get("attempts", []) if a["model"]})
    result.update(type="result", engine_outcome=g.outcome(), steps=g.steps, calls=calls, invalid=invalid,
                  models_returned=returned,
                  agent_score=result["scores"][agent], elapsed=round(clock() - started, 3))
    if trace_path:
        Path(trace_path).parent.mkdir(parents=True, exist_ok=True)
        with open(trace_path, "w", encoding="utf-8") as f:
            for line in [header, *steps, result]:
                f.write(json.dumps(line, ensure_ascii=False) + "\n")
    return header, steps, result


def seed_range(text):
    a, _, b = text.partition("-")
    return range(int(a), int(b or a) + 1)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--player", choices=PLAYERS, required=True)
    p.add_argument("--situation", choices=sorted(SITUATIONS), required=True)
    p.add_argument("--seeds", type=seed_range, required=True, help="e.g. 100-104")
    p.add_argument("--trials", type=int, default=1)
    p.add_argument("--opponents", choices=("heuristic", "random"), default="heuristic")
    p.add_argument("--fixture", action="store_true", help="scripted stand-in instead of a live model")
    p.add_argument("--out", default="traces/scratch")
    args = p.parse_args(argv)

    config, config_hash = load_config()
    model = None
    if args.player.startswith("model"):
        if args.fixture:
            model = FixtureModel()
        else:
            from players.model import VertexModel
            model = VertexModel(config)
    for seed in args.seeds:
        for trial in range(args.trials):
            name = f"{args.player}_{args.situation}_{args.opponents}_s{seed}_t{trial}" + \
                ("_fixture" if args.fixture else "") + ".jsonl"
            header, steps, result = run_episode(seed, args.situation, args.player, args.opponents,
                                                model, config, trial, Path(args.out) / name,
                                                config_hash=config_hash)
            print(f"seed {seed} trial {trial} {args.situation} seat {header['agent_seat']}: "
                  f"{result['reason']} winner={result['winner']} agent_score={result['agent_score']} "
                  f"calls={result['calls']} invalid={result['invalid']} "
                  f"fallbacks={sum(s.get('source') == 'fallback' for s in steps)}")


if __name__ == "__main__":
    main()
