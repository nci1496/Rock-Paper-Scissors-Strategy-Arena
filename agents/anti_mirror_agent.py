from __future__ import annotations

from agent import Agent, Move, RoundContext
from agents.common import ALL_MOVES, beats


class AntiMirrorAgent(Agent):
    @property
    def name(self) -> str:
        return "AntiMirrorAgent"

    def next_move(self, context: RoundContext) -> Move:
        if context.opponent_history:
            return beats(context.opponent_history[-1])
        return context.rng.choice(ALL_MOVES)