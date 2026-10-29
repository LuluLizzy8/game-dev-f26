"""Model-driven player (DESIGN.md §4.2). The prompt is built only from the seat's observation and legal list.

The Vertex call follows the course starter's pattern (course_game/narrator.py @ 66f051b): explicit provider,
env-var settings, HTTP timeout, no automatic retries, no tools.
"""
from dataclasses import dataclass
import hashlib
import json
import os
import time

from doudizhu.engine import label, parse
from doudizhu.view import render

SYSTEM_PROMPT = """You are playing one seat of Dou Dizhu, a three-player climbing card game.
One landlord (20 cards, leads first) plays alone against two peasants who are a team. The first player
to empty their hand wins for their side.

Ranks low to high: 3 4 5 6 7 8 9 10 J Q K A 2 BJ RJ (BJ/RJ = black/red joker). Suits do not matter.
Combinations: single; pair; triple; triple+single; triple+pair; straight of 5+ (3 to A); 3+ consecutive
pairs; 2+ consecutive triples ("plane"), optionally with one single or one pair per triple; four+two
singles; four+two pairs; bomb (four of a rank); rocket (BJ RJ). To follow, play the same kind and length
with a higher main rank, or a bomb, or the rocket; or pass. When both others pass, the last player to
play leads anything. Each bomb or rocket doubles the stakes.

Your teammate (if you are a peasant) is a scripted player with these habits: it leads its lowest
combination, shedding as many cards as it can; it plays the cheapest card set that beats; it does not
beat your plays unless it can go out; it bombs only when an opponent has 4 or fewer cards.

Each turn you get the table and a numbered list of every legal action. Reply with JSON only:
{"action": "<exactly one action string from the list>", "reason": "<at most one short sentence>"}"""

SCHEMA = {
    "type": "object",
    "properties": {"action": {"type": "string"}, "reason": {"type": "string"}},
    "required": ["action"],
}


def build_prompt(obs, legal, variant="model-history", error=None):
    """The whole model input for one turn. R22: model-obs drops the public history."""
    if variant == "model-obs":
        obs = {k: v for k, v in obs.items() if k != "history"}
    lines = [render(obs), "", "Legal actions:"]
    lines += [f"  {i}. {a}" for i, a in enumerate(legal, 1)]
    if error:
        lines += ["", f"Your previous reply was rejected: {error}. Choose again from the list."]
    return "\n".join(lines)


def prompt_hash(text):
    return hashlib.sha256((SYSTEM_PROMPT + "\n" + text).encode()).hexdigest()[:12]


def normalize(text, legal):
    """Match a reply to the legal list; card order and case do not matter (R16). None if no match."""
    if not isinstance(text, str):
        return None
    if text.strip().lower() == "pass":
        return "pass" if "pass" in legal else None
    try:
        action = label(parse(text))
    except KeyError:
        return None
    return action if action in legal else None


@dataclass
class Reply:
    action: str | None  # a legal action string, or None if the reply was unusable
    raw: str | None
    error: str | None  # why the reply was unusable
    api_error: bool  # True if the call itself failed (counts as a call, not an invalid reply)
    latency: float
    input_tokens: int | None = None
    output_tokens: int | None = None
    model: str | None = None


def parse_reply(raw, legal):
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None, "reply was not valid JSON"
    if not isinstance(data, dict) or "action" not in data:
        return None, 'reply must be a JSON object with an "action" field'
    action = normalize(data["action"], legal)
    if action is None:
        return None, f"{data['action']!r} is not in the legal action list"
    return action, None


class FixtureModel:
    """Scripted stand-in for CI and credential-free runs. It is not a model; reports label it 'fixture'."""

    live = False
    model_id = "scripted-fixture-v1"

    def __init__(self, replies=None):
        self.replies = list(replies or [])  # strings or Exceptions, used in order; then legal[0]
        self.prompts = []

    def ask(self, prompt, legal):
        self.prompts.append(prompt)
        started = time.monotonic()
        raw = self.replies.pop(0) if self.replies else json.dumps({"action": legal[0]})
        if isinstance(raw, Exception):
            return Reply(None, None, f"call failed: {type(raw).__name__}", True, time.monotonic() - started,
                         model=self.model_id)
        action, error = parse_reply(raw, legal)
        return Reply(action, raw, error, False, time.monotonic() - started, 0, 0, self.model_id)


class VertexModel:
    live = True

    def __init__(self, config):
        names = ("COURSE_PROVIDER", "COURSE_MODEL", "GOOGLE_CLOUD_PROJECT", "GOOGLE_CLOUD_LOCATION")
        env = {n: os.environ.get(n, "").strip() for n in names}
        missing = [n for n, v in env.items() if not v]
        if missing:
            raise SystemExit(f"Live run needs {', '.join(missing)} set (see README). No fixture substitution.")
        if env["COURSE_PROVIDER"] != "vertex":
            raise SystemExit("This player supports COURSE_PROVIDER=vertex only.")
        from google import genai  # imported here so CI never needs the SDK
        from google.genai import types
        self.types = types
        self.model_id = env["COURSE_MODEL"]
        limits, sampling = config["limits"], config["sampling"]
        self.client = genai.Client(
            vertexai=True, project=env["GOOGLE_CLOUD_PROJECT"], location=env["GOOGLE_CLOUD_LOCATION"],
            http_options=types.HttpOptions(
                timeout=limits["call_timeout_seconds"] * 1000,
                retry_options=types.HttpRetryOptions(attempts=1),
            ),
        )
        self.gen_config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_json_schema=SCHEMA,
            temperature=sampling["temperature"],
            top_p=sampling["top_p"],
            max_output_tokens=sampling["max_output_tokens"],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

    def ask(self, prompt, legal):
        started = time.monotonic()
        try:
            response = self.client.models.generate_content(
                model=self.model_id, contents=prompt, config=self.gen_config)
        except Exception as error:  # timeouts, quota, network: a failed call, counted by the runner
            # Only type and status code: provider messages can contain the project ID, and traces are public.
            code = getattr(error, "code", None) or getattr(error, "status_code", None)
            return Reply(None, None, f"call failed: {type(error).__name__}" + (f" {code}" if code else ""),
                         True, time.monotonic() - started, model=self.model_id)
        latency = time.monotonic() - started
        usage = response.usage_metadata
        tokens_in = getattr(usage, "prompt_token_count", None)
        tokens_out = (getattr(usage, "candidates_token_count", None) or 0) + \
            (getattr(usage, "thoughts_token_count", None) or 0)
        model = response.model_version or self.model_id
        if not response.candidates or response.candidates[0].finish_reason != self.types.FinishReason.STOP:
            return Reply(None, None, "the reply did not complete normally", False, latency, tokens_in, tokens_out, model)
        raw = response.text
        action, error = parse_reply(raw, legal)
        return Reply(action, raw, error, False, latency, tokens_in, tokens_out, model)
