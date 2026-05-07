from __future__ import annotations

from collections import defaultdict, Counter

from agent import Agent, Move, RoundContext
from agents.common import ALL_MOVES, beats


class Markov2Agent(Agent):
    @property
    def name(self) -> str:
        return "Markov2Agent"

    def next_move(self, context: RoundContext) -> Move:
        hist = context.opponent_history
        if len(hist) < 3:
            return context.rng.choice(ALL_MOVES)

        trans = defaultdict(Counter)
        for i in range(2, len(hist)):
            key = (hist[i - 2], hist[i - 1])
            trans[key][hist[i]] += 1

        key = (hist[-2], hist[-1])
        if not trans[key]:
            return context.rng.choice(ALL_MOVES)
        predicted = max(ALL_MOVES, key=lambda m: trans[key][m])
        return beats(predicted)