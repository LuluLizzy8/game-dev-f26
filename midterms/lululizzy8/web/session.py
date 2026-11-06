"""Browser play, same setup as play.py: you take one seat, two heuristic players take the others.

web/index.html loads this file, the engine and the heuristic into Pyodide and calls Session.
Every reply is JSON built only from observe(your seat), so the page never sees another hand (R15).
"""
import json

from doudizhu.engine import DouDizhu
from players import heuristic


class Session:
    def __init__(self, seed, seat):
        self.g = DouDizhu()
        self.g.reset(seed)
        self.seat = seat

    def _bots(self):
        """Play the other seats until it is your turn or the deal ends; one frame per move for the page."""
        g, frames = self.g, []
        while g.outcome()["status"] == "ongoing" and g.turn != self.seat:
            s = g.turn
            g.step(s, heuristic.choose(g.observe(s), g.legal_actions(s)))
            frames.append(g.observe(self.seat))
        return frames

    def _reply(self, frames, **extra):
        g = self.g
        return json.dumps(dict(extra, frames=frames, obs=g.observe(self.seat),
                               legal=g.legal_actions(self.seat), outcome=g.outcome()), ensure_ascii=False)

    def start(self):
        return self._reply(self._bots(), ok=True)

    def play(self, action):
        """Your move as card text in any order ("3 3", "bj bj rj rj") or "pass". A refused move changes nothing."""
        result = self.g.step(self.seat, action)
        if not result["ok"]:
            return self._reply([], ok=False, error=result["error"])
        return self._reply([self.g.observe(self.seat), *self._bots()], ok=True)

    def hint(self):
        """What the heuristic would play from your seat, or None when it is not your turn."""
        legal = self.g.legal_actions(self.seat)
        return heuristic.choose(self.g.observe(self.seat), legal) if legal else None
