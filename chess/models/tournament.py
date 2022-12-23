from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Self

from chess.models.model import Model


class StyleTournament(int, Enum):
    BULLET = 0
    BLITZ = 1,
    FAST_STRIKE = 2


class Tournament(Model):

    def __init__(self,
                 model_id: int = -1,
                 name="",
                 where="",
                 when: date | None = None,
                 style=StyleTournament.BULLET,
                 finished=False) -> None:
        super().__init__(model_id)
        self.name = name
        self.where = where
        self.when = when
        self.style = style
        self.finished = finished

    def __copy__(self):
        return Tournament(
            model_id=self.model_id,
            name=self.name,
            where=self.where,
            when=self.when,
            style=self.style,
            finished=self.finished,
        )

    def update(self, src: Self):
        self.model_id = src.model_id
        self.name = src.name
        self.where = src.where
        self.when = src.when
        self.style = src.style
        self.finished = src.finished
