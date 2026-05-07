from __future__ import annotations

from collections import Counter
from typing import Iterable, Optional, Sequence

from agent import Move

ALL_MOVES = [Move.ROCK, Move.PAPER, Move.SCISSORS]


def beats(move: Move) -> Move:
    if move == Move.ROCK:
        return Move.PAPER
    if move == Move.PAPER:
        return Move.SCISSORS
    return Move.ROCK


def loses_to(move: Move) -> Move:
    if move == Move.ROCK:
        return Move.SCISSORS
    if move == Move.PAPER:
        return Move.ROCK
    return Move.PAPER


def most_common_move(moves: Sequence[Move]) -> Optional[Move]:
    if not moves:
        return None
    counts = Counter(moves)
    return max(ALL_MOVES, key=lambda m: (counts[m], m.value))


def weighted_choice(rng, items: Iterable[tuple[Move, float]]) -> Move:
    pairs = [(m, w) for m, w in items if w > 0]
    if not pairs:
        return rng.choice(ALL_MOVES)
    total = sum(w for _, w in pairs)
    x = rng.random() * total
    upto = 0.0
    for move, weight in pairs:
        upto += weight
        if x <= upto:
            return move
    return pairs[-1][0]