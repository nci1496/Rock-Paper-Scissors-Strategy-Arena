from __future__ import annotations

from collections import Counter, defaultdict

from agent import Agent, Move, RoundContext
from agents.common import ALL_MOVES, beats


class Markov3Agent(Agent):
    @property
    def name(self) -> str:
        return "Markov3Agent"

    def next_move(self, context: RoundContext) -> Move:
        hist = context.opponent_history
        if len(hist) < 2:
            return context.rng.choice(ALL_MOVES)

        if len(hist) >= 4:
            trans3 = defaultdict(Counter)
            for i in range(3, len(hist)):
                key = (hist[i - 3], hist[i - 2], hist[i - 1])
                trans3[key][hist[i]] += 1
            key3 = (hist[-3], hist[-2], hist[-1])
            row3 = trans3[key3]
            if row3:
                predicted3 = max(ALL_MOVES, key=lambda m: row3[m])
                return beats(predicted3)

        if len(hist) >= 3:
            trans2 = defaultdict(Counter)
            for i in range(2, len(hist)):
                key = (hist[i - 2], hist[i - 1])
                trans2[key][hist[i]] += 1
            key2 = (hist[-2], hist[-1])
            row2 = trans2[key2]
            if row2:
                predicted2 = max(ALL_MOVES, key=lambda m: row2[m])
                return beats(predicted2)

        trans1 = defaultdict(Counter)
        for i in range(1, len(hist)):
            trans1[hist[i - 1]][hist[i]] += 1
        row1 = trans1[hist[-1]]
        if row1:
            predicted1 = max(ALL_MOVES, key=lambda m: row1[m])
            return beats(predicted1)

        return context.rng.choice(ALL_MOVES)
