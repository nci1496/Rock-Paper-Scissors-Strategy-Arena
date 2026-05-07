from __future__ import annotations

from agent import Agent, Move, RoundContext, RoundFeedback
from agents.common import ALL_MOVES, beats


class LoseShiftWinStayAgent(Agent):
    def __init__(self) -> None:
        self._last_move: Move | None = None
        self._last_outcome: int = 0

    @property
    def name(self) -> str:
        return "LoseShiftWinStayAgent"

    def next_move(self, context: RoundContext) -> Move:
        if self._last_move is None:
            return context.rng.choice(ALL_MOVES)
        if self._last_outcome >= 0:
            return self._last_move
        return beats(self._last_move)

    def on_round_end(self, feedback: RoundFeedback) -> None:
        self._last_move = feedback.my_move
        self._last_outcome = feedback.outcome

    def reset(self) -> None:
        self._last_move = None
        self._last_outcome = 0