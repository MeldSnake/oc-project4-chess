from __future__ import annotations

from datetime import date
from enum import Enum
from typing import TYPE_CHECKING, Self

from chess.models.model import Model

if TYPE_CHECKING:
    from chess.models.round import Round
    from chess.models.player import Player


class StyleTournament(int, Enum):
    BULLET = 0
    BLITZ = 1,
    FAST_STRIKE = 2


class Tournament(Model):

    @property
    def scores(self):
        score_player: dict[Player, float] = {}
        for round_ in self.rounds:
            for player, score in round_.scores.items():
                if player and player not in score_player:
                    score_player[player] = score
                else:
                    score_player[player] += score
        return score_player

    @property
    def finished(self):
        if len(self.rounds) == self.round_count:
            return all([x.finished for x in self.rounds])
        return False

    @property
    def winner(self):
        if self.finished:
            pass
        return max(self.scores.items(), key=lambda x: x[1])[0]

    def __init__(self,
                 model_id: int = -1,
                 name="",
                 where="",
                 when: date | None = None,
                 style=StyleTournament.BULLET,
                 round_count=4,
                 rounds: list[Round] = []) -> None:
        super().__init__(model_id)
        self.name = name
        self.where = where
        self.when = when or date(1, 1, 1)
        self.style = style
        self.round_count = round_count
        self.rounds: list[Round] = list(rounds)

    def __copy__(self):
        return Tournament(
            model_id=self.model_id,
            name=self.name,
            where=self.where,
            when=self.when,
            round_count=self.round_count,
            style=self.style,
            rounds=self.rounds,
        )

    def update(self, src: Self):
        self.model_id = src.model_id
        self.name = src.name
        self.where = src.where
        self.when = src.when
        self.round_count = src.round_count
        self.style = src.style
        self.rounds = src.rounds
