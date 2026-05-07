from __future__ import annotations

from agent import Agent, Move, RoundContext
from agents.common import beats, most_common_move


class FrequencyCounterAgent(Agent):
    @property
    def name(self) -> str:
        return "FrequencyCounterAgent"

    def next_move(self, context: RoundContext) -> Move:
        target = most_common_move(context.opponent_history)
        if target is None:
            return context.rng.choice([Move.ROCK, Move.PAPER, Move.SCISSORS])
        return beats(target)