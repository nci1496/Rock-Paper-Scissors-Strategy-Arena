from __future__ import annotations

from agent import Agent, Move, RoundContext
from agents.common import ALL_MOVES


class FakePatternAgent(Agent):
    def __init__(self, fake_len: int = 6) -> None:
        self.fake_len = fake_len
        self._idx = 0
        self._seq = [Move.ROCK, Move.PAPER, Move.SCISSORS]

    @property
    def name(self) -> str:
        return "FakePatternAgent"

    def next_move(self, context: RoundContext) -> Move:
        if len(context.my_history) < self.fake_len:
            move = self._seq[self._idx]
            self._idx = (self._idx + 1) % len(self._seq)
            return move
        if context.rng.random() < 0.35:
            return context.rng.choice(ALL_MOVES)
        move = self._seq[self._idx]
        self._idx = (self._idx + 1) % len(self._seq)
        return move

    def reset(self) -> None:
        self._idx = 0