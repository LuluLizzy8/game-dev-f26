"""Comparison table from trace files (DESIGN.md §6 metrics).

    python report.py traces/heldout --out results/heldout.md
"""
import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path


def load(dirs):
    episodes = []
    for d in dirs:
        for path in sorted(Path(d).rglob("*.jsonl")):
            lines = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
            header, result = lines[0], lines[-1]
            steps = [l for l in lines if l["type"] == "step"]
            episodes.append({"header": header, "steps": steps, "result": result, "path": str(path)})
    return episodes


def won(ep):
    return ep["result"]["agent_score"] > 0


def pct(values, q):
    values = sorted(values)
    return values[min(len(values) - 1, int(q * len(values)))] if values else None


def summarize(group, baseline):
    attempts = [a for ep in group for s in ep["steps"] for a in s.get("attempts", [])]
    latencies = [a["latency"] for a in attempts if not a["api_error"]]
    sources = [s.get("source") for ep in group for s in ep["steps"] if s["seat"] == ep["header"]["agent_seat"]]
    reasons = defaultdict(int)
    for ep in group:
        reasons[ep["result"]["reason"]] += 1
    clean = [ep for ep in group if not any(s.get("source") == "fallback" for s in ep["steps"])]
    row = {
        "episodes": len(group),
        "wins": sum(won(ep) for ep in group),
        "losses": sum(not won(ep) and ep["result"]["winner"] is not None for ep in group),
        "no_result": reasons["step_limit"],
        "call_limit": reasons["call_limit"], "timeout": reasons["timeout"], "invalid_limit": reasons["invalid_limit"],
        "mean_score": round(statistics.mean(ep["result"]["agent_score"] for ep in group), 2),
        "fallback_free_wins": f"{sum(won(ep) for ep in clean)}/{len(clean)}",
        "invalid_replies": sum(ep["result"]["invalid"] for ep in group),
        "api_errors": sum(a["api_error"] for a in attempts),
        "fallbacks": sources.count("fallback"),
        "forced": sources.count("forced"),
        "calls": sum(ep["result"]["calls"] for ep in group),
        "latency_median_s": round(statistics.median(latencies), 2) if latencies else "-",
        "latency_p95_s": round(pct(latencies, 0.95), 2) if latencies else "-",
        "tokens_in": sum(a["input_tokens"] or 0 for a in attempts),
        "tokens_out": sum(a["output_tokens"] or 0 for a in attempts),
    }
    # Paired comparison with the heuristic on the same (seed, situation, opponents), trial 0 of the baseline.
    diffs, discordant = [], 0
    for ep in group:
        h = ep["header"]
        base = baseline.get((h["seed"], h["situation"], h["opponents"]))
        if base and h["player"] != "heuristic":
            diffs.append(ep["result"]["agent_score"] - base["result"]["agent_score"])
            discordant += won(ep) != won(base)
    row["paired_diff_vs_heuristic"] = round(statistics.mean(diffs), 2) if diffs else "-"
    row["discordant_pairs"] = f"{discordant}/{len(diffs)}" if diffs else "-"
    return row


def table(episodes):
    baseline = {}
    for ep in episodes:
        h = ep["header"]
        if h["player"] == "heuristic" and h["trial"] == 0:
            baseline[(h["seed"], h["situation"], h["opponents"])] = ep
    groups = defaultdict(list)
    for ep in episodes:
        h = ep["header"]
        groups[(h["player"], "live" if h["live"] else ("fixture" if h["player"].startswith("model") else "-"),
                h["model"] or "-", h["situation"], h["opponents"])].append(ep)
    rows = []
    for key in sorted(groups):
        seeds = sorted({ep["header"]["seed"] for ep in groups[key]})
        rows.append(dict(zip(("player", "mode", "model", "situation", "opponents"), key),
                         seeds=f"{seeds[0]}-{seeds[-1]}", **summarize(groups[key], baseline)))
    if not rows:
        return "No traces found.\n"
    cols = list(rows[0])
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(str(r[c]) for c in cols) + " |" for r in rows]
    commits = sorted({ep["header"]["game_commit"] for ep in episodes})
    configs = sorted({ep["header"]["config_hash"] for ep in episodes})
    out += ["", f"Game commits: {', '.join(commits)}. Config hashes: {', '.join(configs)}.",
            "Tokens are as reported by the API; cost = tokens x the dated price recorded in EVALUATION.md."]
    return "\n".join(out) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("dirs", nargs="+")
    p.add_argument("--out", help="write UTF-8 markdown here instead of printing")
    args = p.parse_args(argv)
    text = table(load(args.dirs))
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        print(text)


if __name__ == "__main__":
    main()
