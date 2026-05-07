from __future__ import annotations

from collections import Counter, defaultdict

from agent import Agent, Move, RoundContext, RoundFeedback
from agents.common import ALL_MOVES, beats, most_common_move


class ScoreBasedAgent(Agent):
    def __init__(self) -> None:
        self.scores = defaultdict(float)

    @property
    def name(self) -> str:
        return "ScoreBasedAgent"

    def _frequency_counter_pick(self, context: RoundContext) -> Move:
        target = most_common_move(context.opponent_history)
        if target is None:
            return context.rng.choice(ALL_MOVES)
        return beats(target)

    def _markov3_pick(self, context: RoundContext) -> Move:
        hist = context.opponent_history
        if len(hist) < 3:
            return context.rng.choice(ALL_MOVES)

        trans2: dict[tuple[Move, Move], Counter[Move]] = defaultdict(Counter)
        for i in range(2, len(hist)):
            key = (hist[i - 2], hist[i - 1])
            trans2[key][hist[i]] += 1

        key = (hist[-2], hist[-1])
        row = trans2[key]
        if not row:
            return self._frequency_counter_pick(context)
        predicted = max(ALL_MOVES, key=lambda m: row[m])
        return beats(predicted)

    def _candidates(self, context: RoundContext) -> dict[str, Move]:
        random_pick = context.rng.choice(ALL_MOVES)
        mirror = context.opponent_history[-1] if context.opponent_history else random_pick
        anti_mirror = beats(mirror)
        frequency_counter = self._frequency_counter_pick(context)
        markov3_counter = self._markov3_pick(context)
        return {
            "random": random_pick,
            "mirror": mirror,
            "anti_mirror": anti_mirror,
            "frequency_counter": frequency_counter,
            "markov3_counter": markov3_counter,
        }

    def next_move(self, context: RoundContext) -> Move:
        c = self._candidates(context)
        best_name = max(c.keys(), key=lambda k: self.scores[k])
        if self.scores[best_name] == 0 and context.rng.random() < 0.4:
            best_name = context.rng.choice(list(c.keys()))
        self._last_choice = best_name
        return c[best_name]

    def on_round_end(self, feedback: RoundFeedback) -> None:
        if hasattr(self, "_last_choice"):
            self.scores[self._last_choice] += feedback.outcome

    def reset(self) -> None:
        self._last_choice = "random"
