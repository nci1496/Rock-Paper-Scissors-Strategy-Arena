from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
import random

from agent import Agent, Move, RoundContext, RoundFeedback


@dataclass(frozen=True)
class RoundRecord:
    round_index: int
    move_a: Move
    move_b: Move
    outcome: int


@dataclass(frozen=True)
class MatchResult:
    agent_a_name: str
    agent_b_name: str
    rounds: int
    wins_a: int
    wins_b: int
    draws: int
    win_rate_a: float
    win_rate_b: float
    draw_rate: float
    net_wins_a: int
    seed: Optional[int]
    records: List[RoundRecord]


def judge_round(move_a: Move, move_b: Move) -> int:
    if move_a == move_b:
        return 0

    winning_pairs = {
        (Move.ROCK, Move.SCISSORS),
        (Move.PAPER, Move.ROCK),
        (Move.SCISSORS, Move.PAPER),
    }
    return 1 if (move_a, move_b) in winning_pairs else -1


def run_match(
    agent_a: Agent,
    agent_b: Agent,
    rounds: int = 1000,
    seed: Optional[int] = None,
    reset_agents: bool = True,
) -> MatchResult:
    if rounds <= 0:
        raise ValueError("rounds must be a positive integer")

    rng = random.Random(seed)
    if reset_agents:
        agent_a.reset()
        agent_b.reset()

    history_a: List[Move] = []
    history_b: List[Move] = []
    records: List[RoundRecord] = []

    wins_a = 0
    wins_b = 0
    draws = 0

    for idx in range(1, rounds + 1):
        context_a = RoundContext(
            round_index=idx,
            total_rounds=rounds,
            my_history=tuple(history_a),
            opponent_history=tuple(history_b),
            rng=rng,
        )
        context_b = RoundContext(
            round_index=idx,
            total_rounds=rounds,
            my_history=tuple(history_b),
            opponent_history=tuple(history_a),
            rng=rng,
        )

        move_a = agent_a.next_move(context_a)
        move_b = agent_b.next_move(context_b)
        outcome = judge_round(move_a, move_b)

        if outcome == 1:
            wins_a += 1
        elif outcome == -1:
            wins_b += 1
        else:
            draws += 1

        history_a.append(move_a)
        history_b.append(move_b)

        agent_a.on_round_end(
            RoundFeedback(
                round_index=idx,
                my_move=move_a,
                opponent_move=move_b,
                outcome=outcome,
            )
        )
        agent_b.on_round_end(
            RoundFeedback(
                round_index=idx,
                my_move=move_b,
                opponent_move=move_a,
                outcome=-outcome,
            )
        )

        records.append(RoundRecord(idx, move_a, move_b, outcome))

    return MatchResult(
        agent_a_name=agent_a.name,
        agent_b_name=agent_b.name,
        rounds=rounds,
        wins_a=wins_a,
        wins_b=wins_b,
        draws=draws,
        win_rate_a=wins_a / rounds,
        win_rate_b=wins_b / rounds,
        draw_rate=draws / rounds,
        net_wins_a=wins_a - wins_b,
        seed=seed,
        records=records,
    )
