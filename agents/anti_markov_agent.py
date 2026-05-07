from __future__ import annotations

from collections import Counter, defaultdict

from agent import Agent, Move, RoundContext
from agents.common import ALL_MOVES, beats, most_common_move


class AntiMarkovAgent(Agent):
    @property
    def name(self) -> str:
        return "AntiMarkovAgent"

    def _predict_next_with_markov2(self, history: tuple[Move, ...]) -> tuple[Move, float]:
        if len(history) < 2:
            if not history:
                return Move.ROCK, 0.0
            return history[-1], 0.2

        trans2 = defaultdict(Counter)
        for i in range(2, len(history)):
            key = (history[i - 2], history[i - 1])
            trans2[key][history[i]] += 1

        key = (history[-2], history[-1])
        row2 = trans2[key]
        if row2:
            total2 = sum(row2.values())
            predicted2 = max(ALL_MOVES, key=lambda m: row2[m])
            confidence2 = row2[predicted2] / total2
            return predicted2, confidence2

        trans1 = defaultdict(Counter)
        for i in range(1, len(history)):
            trans1[history[i - 1]][history[i]] += 1
        row1 = trans1[history[-1]]
        if row1:
            total1 = sum(row1.values())
            predicted1 = max(ALL_MOVES, key=lambda m: row1[m])
            confidence1 = row1[predicted1] / total1 * 0.9
            return predicted1, confidence1

        fallback = most_common_move(history)
        if fallback is None:
            return Move.ROCK, 0.0
        return fallback, 0.25

    def next_move(self, context: RoundContext) -> Move:
        # DelayedCounter-like anti-Markov logic, but without any random-move phase.
        opp_next, opp_conf = self._predict_next_with_markov2(context.opponent_history)
        direct_counter = beats(opp_next)

        my_next_as_seen_by_opp, my_conf = self._predict_next_with_markov2(context.my_history)
        opponent_meta_move = beats(my_next_as_seen_by_opp)
        meta_counter = beats(opponent_meta_move)

        if my_conf >= opp_conf and my_conf >= 0.4:
            return meta_counter
        return direct_counter
