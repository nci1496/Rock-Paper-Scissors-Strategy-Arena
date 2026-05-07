from __future__ import annotations

from collections import Counter

from agent import Agent, Move, RoundContext
from agents.common import ALL_MOVES, beats


class AdaptiveMixAgent(Agent):
    def __init__(self, window_size: int = 5, global_weight: float = 0.4, local_weight: float = 0.6) -> None:
        self.window_size = window_size
        self.global_weight = global_weight
        self.local_weight = local_weight

    @property
    def name(self) -> str:
        return "AdaptiveMixAgent"

    def next_move(self, context: RoundContext) -> Move:
        if not context.opponent_history:
            return context.rng.choice(ALL_MOVES)

        global_counts = Counter(context.opponent_history)
        local_counts = Counter(context.opponent_history[-self.window_size:])

        best = max(
            ALL_MOVES,
            key=lambda m: self.global_weight * global_counts[m] + self.local_weight * local_counts[m],
        )
        return beats(best)