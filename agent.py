from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Tuple
import random


class Move(Enum):
    ROCK = "rock"
    PAPER = "paper"
    SCISSORS = "scissors"


@dataclass(frozen=True)
class RoundContext:
    round_index: int
    total_rounds: int
    my_history: Tuple[Move, ...]
    opponent_history: Tuple[Move, ...]
    rng: random.Random


@dataclass(frozen=True)
class RoundFeedback:
    round_index: int
    my_move: Move
    opponent_move: Move
    outcome: int


class Agent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def next_move(self, context: RoundContext) -> Move:
        raise NotImplementedError

    def on_round_end(self, feedback: RoundFeedback) -> None:
        return None

    def reset(self) -> None:
        return None