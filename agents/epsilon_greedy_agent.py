from __future__ import annotations

from collections import Counter

from agent import Agent, Move, RoundContext
from agents.common import ALL_MOVES, beats


class EpsilonGreedyAgent(Agent):
    def __init__(self, epsilon: float = 0.1) -> None:
        self.epsilon = epsilon

    @property
    def name(self) -> str:
        return "EpsilonGreedyAgent"

    def next_move(self, context: RoundContext) -> Move:
        if context.rng.random() < self.epsilon or not context.opponent_history:
            return context.rng.choice(ALL_MOVES)

        counts = Counter(context.opponent_history)
        most = max(ALL_MOVES, key=lambda m: counts[m])
        return beats(most)