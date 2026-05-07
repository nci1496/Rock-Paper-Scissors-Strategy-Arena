from __future__ import annotations

from agent import Agent, Move, RoundContext
from agents.common import weighted_choice


class BiasedRandomAgent(Agent):
    @property
    def name(self) -> str:
        return "BiasedRandomAgent"

    def next_move(self, context: RoundContext) -> Move:
        return weighted_choice(
            context.rng,
            [
                (Move.ROCK, 0.5),
                (Move.PAPER, 0.25),
                (Move.SCISSORS, 0.25),
            ],
        )