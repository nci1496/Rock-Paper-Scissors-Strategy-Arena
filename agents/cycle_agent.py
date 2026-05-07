from __future__ import annotations

from agent import Agent, Move, RoundContext


class CycleAgent(Agent):
    def __init__(self) -> None:
        self._index = 0
        self._sequence = [Move.ROCK, Move.PAPER, Move.SCISSORS]

    @property
    def name(self) -> str:
        return "CycleAgent"

    def next_move(self, context: RoundContext) -> Move:
        move = self._sequence[self._index]
        self._index = (self._index + 1) % len(self._sequence)
        return move

    def reset(self) -> None:
        self._index = 0