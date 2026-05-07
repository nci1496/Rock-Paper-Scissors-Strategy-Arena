from __future__ import annotations

from agent import Agent, Move, RoundContext
from agents.common import ALL_MOVES, beats


class BeatLastWinnerAgent(Agent):
    @property
    def name(self) -> str:
        return "BeatLastWinnerAgent"

    def next_move(self, context: RoundContext) -> Move:
        if not context.opponent_history:
            return context.rng.choice(ALL_MOVES)
        return beats(context.opponent_history[-1])