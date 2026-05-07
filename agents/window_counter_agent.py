from __future__ import annotations

from agent import Agent, Move, RoundContext
from agents.common import beats, most_common_move


class WindowCounterAgent(Agent):
    def __init__(self, window_size: int = 5) -> None:
        self.window_size = window_size

    @property
    def name(self) -> str:
        return f"WindowCounterAgent(N={self.window_size})"

    def next_move(self, context: RoundContext) -> Move:
        window = context.opponent_history[-self.window_size:]
        target = most_common_move(window)
        if target is None:
            return context.rng.choice([Move.ROCK, Move.PAPER, Move.SCISSORS])
        return beats(target)