from __future__ import annotations

from collections import defaultdict, Counter

from agent import Agent, Move, RoundContext
from agents.common import ALL_MOVES, beats


class Markov1Agent(Agent):
    @property
    def name(self) -> str:
        return "Markov1Agent"

    def next_move(self, context: RoundContext) -> Move:
        hist = context.opponent_history
        if len(hist) < 2:
            return context.rng.choice(ALL_MOVES)

        trans = defaultdict(Counter)
        for i in range(1, len(hist)):
            trans[hist[i - 1]][hist[i]] += 1

        last = hist[-1]
        if not trans[last]:
            return context.rng.choice(ALL_MOVES)
        predicted = max(ALL_MOVES, key=lambda m: trans[last][m])
        return beats(predicted)