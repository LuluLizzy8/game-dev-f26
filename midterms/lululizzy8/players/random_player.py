"""Uniform random over legal actions: the floor that shows whether the heuristic is strong."""
import random


class RandomPlayer:
    def __init__(self, seed):
        self.rng = random.Random(seed)

    def choose(self, obs, legal):
        return self.rng.choice(legal)
