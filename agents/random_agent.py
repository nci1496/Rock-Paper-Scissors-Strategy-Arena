from __future__ import annotations

from agent import Agent, Move, RoundContext


class RandomAgent(Agent):
    @property
    def name(self) -> str:
        return "RandomAgent"

    def next_move(self, context: RoundContext) -> Move:
        return context.rng.choice([Move.ROCK, Move.PAPER, Move.SCISSORS])