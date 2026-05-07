from __future__ import annotations

from collections import Counter

from agent import Agent, Move, RoundContext
from agents.common import ALL_MOVES, beats


class StrategyPoolAgent(Agent):
    @property
    def name(self) -> str:
        return "StrategyPoolAgent"

    def _random_pick(self, context: RoundContext) -> Move:
        return context.rng.choice(ALL_MOVES)

    def _frequency_pick(self, context: RoundContext) -> Move:
        if not context.opponent_history:
            return self._random_pick(context)
        counts = Counter(context.opponent_history)
        return beats(max(ALL_MOVES, key=lambda m: counts[m]))

    def _markov1_pick(self, context: RoundContext) -> Move:
        hist = context.opponent_history
        if len(hist) < 2:
            return self._random_pick(context)
        last = hist[-1]
        next_moves = [hist[i] for i in range(1, len(hist)) if hist[i - 1] == last]
        if not next_moves:
            return self._random_pick(context)
        counts = Counter(next_moves)
        return beats(max(ALL_MOVES, key=lambda m: counts[m]))

    def next_move(self, context: RoundContext) -> Move:
        picker = context.rng.choice([self._random_pick, self._frequency_pick, self._markov1_pick])
        return picker(context)