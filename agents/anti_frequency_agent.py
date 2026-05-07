from __future__ import annotations

from collections import Counter

from agent import Agent, Move, RoundContext
from agents.common import ALL_MOVES, beats


class AntiFrequencyAgent(Agent):
    @property
    def name(self) -> str:
        return "AntiFrequencyAgent"

    def next_move(self, context: RoundContext) -> Move:
        if not context.my_history:
            return context.rng.choice(ALL_MOVES)

        my_counts = Counter(context.my_history)
        least_used = min(ALL_MOVES, key=lambda m: (my_counts[m], m.value))
        if context.rng.random() < 0.8:
            return least_used
        return beats(least_used)