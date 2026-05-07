from __future__ import annotations

from collections import Counter, deque
import math

from agent import Agent, Move, RoundContext, RoundFeedback
from agents.common import ALL_MOVES, beats, most_common_move


class RegretMatchingAgent(Agent):
    """
    Strategy-level regret learner with EXP3-style adversarial update.

    Upgrades included:
    - strategy-level learning (not just action-level)
    - exponential forgetting / decay
    - softmax over clipped regrets for stability
    - epsilon floor to avoid over-confident collapse
    - short-term rolling window adaptation
    - predictability + exploit + drift detection -> adaptive exploration
    """

    def __init__(
        self,
        decay: float = 0.97,
        epsilon_min: float = 0.06,
        epsilon_max: float = 0.35,
        exp3_gamma: float = 0.12,
        regret_clip: float = 6.0,
        temperature: float = 1.25,
        window_k: int = 36,
        loss_streak_trigger: int = 4,
    ) -> None:
        self.decay = decay
        self.epsilon_min = epsilon_min
        self.epsilon_max = epsilon_max
        self.exp3_gamma_base = exp3_gamma
        self.regret_clip = regret_clip
        self.temperature = temperature
        self.window_k = window_k
        self.loss_streak_trigger = loss_streak_trigger

        self._strategy_names = [
            "random",
            "frequency_counter",
            "markov2_counter",
            "anti_mirror",
            "anti_frequency_mix",
        ]

        self._regret = {name: 0.0 for name in self._strategy_names}
        self._weights = {name: 1.0 for name in self._strategy_names}
        self._recent = deque(maxlen=window_k)
        self._loss_streak = 0

        self._last_context: RoundContext | None = None
        self._last_choice: str | None = None
        self._last_probs: dict[str, float] = {}
        self._last_opp_pred: Move | None = None

    @property
    def name(self) -> str:
        return "RegretMatchingAgent"

    @staticmethod
    def _utility(my_move: Move, opp_move: Move) -> float:
        if my_move == opp_move:
            return 0.0
        if (my_move == Move.ROCK and opp_move == Move.SCISSORS) or (my_move == Move.PAPER and opp_move == Move.ROCK) or (my_move == Move.SCISSORS and opp_move == Move.PAPER):
            return 1.0
        return -1.0

    def _predict_opp_next(self, context: RoundContext) -> Move | None:
        hist = context.opponent_history
        if len(hist) >= 3:
            trans2: dict[tuple[Move, Move], Counter[Move]] = {}
            for i in range(2, len(hist)):
                key = (hist[i - 2], hist[i - 1])
                trans2.setdefault(key, Counter())
                trans2[key][hist[i]] += 1
            key2 = (hist[-2], hist[-1])
            row = trans2.get(key2)
            if row:
                return max(ALL_MOVES, key=lambda m: row[m])
        return most_common_move(hist)

    def _strategy_action(self, name: str, context: RoundContext) -> Move:
        if name == "random":
            return context.rng.choice(ALL_MOVES)

        if name == "frequency_counter":
            target = most_common_move(context.opponent_history)
            return beats(target) if target is not None else context.rng.choice(ALL_MOVES)

        if name == "markov2_counter":
            pred = self._predict_opp_next(context)
            return beats(pred) if pred is not None else context.rng.choice(ALL_MOVES)

        if name == "anti_mirror":
            if context.opponent_history:
                return beats(context.opponent_history[-1])
            return context.rng.choice(ALL_MOVES)

        # anti_frequency_mix
        if not context.my_history:
            return context.rng.choice(ALL_MOVES)
        counts = Counter(context.my_history)
        least_used = min(ALL_MOVES, key=lambda m: (counts[m], m.value))
        return least_used

    def _opponent_drift_score(self, context: RoundContext) -> float:
        hist = context.opponent_history
        if len(hist) < self.window_k:
            return 0.0
        half = self.window_k // 2
        old = Counter(hist[-self.window_k : -half])
        new = Counter(hist[-half:])
        total_old = max(1, sum(old.values()))
        total_new = max(1, sum(new.values()))
        l1 = 0.0
        for m in ALL_MOVES:
            l1 += abs(old[m] / total_old - new[m] / total_new)
        return l1 / 2.0

    def _predictability_penalty(self) -> float:
        if len(self._recent) < 10:
            return 0.0
        # recent item: (outcome, chosen_strategy, pred_hit)
        hits = sum(1 for _, _, hit in self._recent if hit)
        acc = hits / len(self._recent)
        # low predictability => boost exploration
        return max(0.0, 0.35 - acc)

    def _adaptive_epsilon(self, context: RoundContext) -> float:
        eps = self.epsilon_min
        if self._loss_streak >= self.loss_streak_trigger:
            eps += 0.10
        eps += min(0.16, self._opponent_drift_score(context) * 0.30)
        eps += min(0.12, self._predictability_penalty())
        return max(self.epsilon_min, min(self.epsilon_max, eps))

    def _strategy_probs(self, context: RoundContext) -> dict[str, float]:
        # clip regrets and softmax for stable policy synthesis
        clipped = {k: max(-self.regret_clip, min(self.regret_clip, v)) for k, v in self._regret.items()}
        logits = {k: clipped[k] / max(1e-6, self.temperature) for k in self._strategy_names}
        max_logit = max(logits.values())
        expv = {k: math.exp(logits[k] - max_logit) * self._weights[k] for k in self._strategy_names}
        z = sum(expv.values())
        base = {k: expv[k] / z for k in self._strategy_names}

        eps = self._adaptive_epsilon(context)
        n = len(self._strategy_names)
        return {k: (1.0 - eps) * base[k] + eps / n for k in self._strategy_names}

    def next_move(self, context: RoundContext) -> Move:
        probs = self._strategy_probs(context)
        x = context.rng.random()
        upto = 0.0
        choice = self._strategy_names[-1]
        for name in self._strategy_names:
            upto += probs[name]
            if x <= upto:
                choice = name
                break

        move = self._strategy_action(choice, context)

        self._last_context = context
        self._last_choice = choice
        self._last_probs = probs
        self._last_opp_pred = self._predict_opp_next(context)
        return move

    def on_round_end(self, feedback: RoundFeedback) -> None:
        if self._last_context is None or self._last_choice is None:
            return

        # decay / forgetting: prevent historical lock-in
        for k in self._strategy_names:
            self._regret[k] *= self.decay
            self._weights[k] = max(1e-6, self._weights[k] * (0.5 + 0.5 * self.decay))

        opp = feedback.opponent_move
        actual = self._utility(feedback.my_move, opp)

        # strategy-level counterfactual regrets, then clipped
        per_strategy_reward: dict[str, float] = {}
        for s in self._strategy_names:
            alt = self._strategy_action(s, self._last_context)
            r = self._utility(alt, opp)
            per_strategy_reward[s] = r
            self._regret[s] += r - actual
            self._regret[s] = max(-self.regret_clip, min(self.regret_clip, self._regret[s]))

        # EXP3 adversarial update on chosen strategy
        chosen = self._last_choice
        p = max(1e-6, self._last_probs.get(chosen, 1.0 / len(self._strategy_names)))
        reward01 = (per_strategy_reward[chosen] + 1.0) / 2.0
        est_reward = reward01 / p
        gamma = self.exp3_gamma_base
        self._weights[chosen] *= math.exp((gamma * est_reward) / len(self._strategy_names))

        # exploit detection (loss streak)
        if feedback.outcome == -1:
            self._loss_streak += 1
        else:
            self._loss_streak = 0

        pred_hit = self._last_opp_pred is not None and self._last_opp_pred == opp
        self._recent.append((feedback.outcome, chosen, pred_hit))

    def reset(self) -> None:
        self._regret = {name: 0.0 for name in self._strategy_names}
        self._weights = {name: 1.0 for name in self._strategy_names}
        self._recent.clear()
        self._loss_streak = 0
        self._last_context = None
        self._last_choice = None
        self._last_probs = {}
        self._last_opp_pred = None