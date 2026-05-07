from __future__ import annotations

from collections import Counter

from agent import Agent, Move, RoundContext
from agents.common import ALL_MOVES, beats


class EnsembleAgent(Agent):
    @property
    def name(self) -> str:
        return "EnsembleAgent"

    def next_move(self, context: RoundContext) -> Move:
        votes: list[Move] = []

        votes.append(context.rng.choice(ALL_MOVES))

        if context.opponent_history:
            counts = Counter(context.opponent_history)
            votes.append(beats(max(ALL_MOVES, key=lambda m: counts[m])))
        else:
            votes.append(context.rng.choice(ALL_MOVES))

        if len(context.opponent_history) >= 2:
            last = context.opponent_history[-1]
            following = [context.opponent_history[i] for i in range(1, len(context.opponent_history)) if context.opponent_history[i - 1] == last]
            if following:
                f_counts = Counter(following)
                votes.append(beats(max(ALL_MOVES, key=lambda m: f_counts[m])))
            else:
                votes.append(context.rng.choice(ALL_MOVES))
        else:
            votes.append(context.rng.choice(ALL_MOVES))

        v_counts = Counter(votes)
        return max(ALL_MOVES, key=lambda m: v_counts[m])