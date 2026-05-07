from __future__ import annotations

from agent import Agent, Move, RoundContext


class RockOnlyAgent(Agent):
    @property
    def name(self) -> str:
        return "RockOnlyAgent"

    def next_move(self, context: RoundContext) -> Move:
        return Move.ROCK