from __future__ import annotations

from agent import Agent, Move, RoundContext
from agents.common import ALL_MOVES, beats


class CycleDetectorAgent(Agent):
    @property
    def name(self) -> str:
        return "CycleDetectorAgent"

    def _detect_period(self, history: tuple[Move, ...], max_period: int = 6) -> int:
        n = len(history)
        for p in range(1, min(max_period, n // 2) + 1):
            a = history[-p:]
            b = history[-2 * p : -p]
            if a == b:
                return p
        return 0

    def next_move(self, context: RoundContext) -> Move:
        hist = context.opponent_history
        period = self._detect_period(hist)
        if period > 0 and len(hist) >= period:
            predicted = hist[-period]
            return beats(predicted)
        return context.rng.choice(ALL_MOVES)