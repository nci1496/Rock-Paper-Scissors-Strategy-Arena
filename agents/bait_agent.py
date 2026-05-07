from __future__ import annotations

from collections import Counter

from agent import Agent, Move, RoundContext
from agents.common import ALL_MOVES, loses_to, beats


class BaitAgent(Agent):
    def __init__(self, bait_rounds: int = 6) -> None:
        self.bait_rounds = bait_rounds

    @property
    def name(self) -> str:
        return "BaitAgent"

    def next_move(self, context: RoundContext) -> Move:
        if not context.opponent_history:
            return context.rng.choice(ALL_MOVES)

        counts = Counter(context.opponent_history)
        likely = max(ALL_MOVES, key=lambda m: counts[m])

        if len(context.my_history) < self.bait_rounds:
            return loses_to(likely)
        return beats(likely)