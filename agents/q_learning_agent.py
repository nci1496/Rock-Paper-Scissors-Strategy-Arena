from __future__ import annotations

from collections import defaultdict

from agent import Agent, Move, RoundContext, RoundFeedback
from agents.common import ALL_MOVES


class QLearningAgent(Agent):
    def __init__(
        self,
        alpha: float = 0.18,
        gamma: float = 0.92,
        epsilon_start: float = 0.25,
        epsilon_min: float = 0.03,
        epsilon_decay: float = 0.997,
        optimistic_q: float = 0.15,
    ) -> None:
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon_start = epsilon_start
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.optimistic_q = optimistic_q
        self.epsilon = epsilon_start
        self.q = defaultdict(lambda: {m: optimistic_q for m in ALL_MOVES})
        self._last_state: tuple[Move | None, Move | None, Move | None] | None = None
        self._last_action: Move | None = None
        self._steps = 0

    @property
    def name(self) -> str:
        return "QLearningAgent"

    def _state(self, context: RoundContext) -> tuple[Move | None, Move | None, Move | None]:
        opp_last = context.opponent_history[-1] if len(context.opponent_history) >= 1 else None
        opp_prev = context.opponent_history[-2] if len(context.opponent_history) >= 2 else None
        my_last = context.my_history[-1] if len(context.my_history) >= 1 else None
        return (opp_last, opp_prev, my_last)

    def next_move(self, context: RoundContext) -> Move:
        state = self._state(context)
        if context.rng.random() < self.epsilon:
            action = context.rng.choice(ALL_MOVES)
        else:
            action = max(ALL_MOVES, key=lambda m: self.q[state][m])
        self._last_state = state
        self._last_action = action
        return action

    def on_round_end(self, feedback: RoundFeedback) -> None:
        if self._last_action is None or self._last_state is None:
            return

        if feedback.outcome == 1:
            reward = 1.0
        elif feedback.outcome == -1:
            reward = -1.0
        else:
            reward = 0.1

        next_state = (feedback.opponent_move, self._last_state[0], feedback.my_move)
        old_q = self.q[self._last_state][self._last_action]
        best_next = max(self.q[next_state].values())
        self.q[self._last_state][self._last_action] = old_q + self.alpha * (reward + self.gamma * best_next - old_q)
        self._steps += 1
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def reset(self) -> None:
        self._last_state = None
        self._last_action = None
        self._steps = 0
        self.epsilon = self.epsilon_start
