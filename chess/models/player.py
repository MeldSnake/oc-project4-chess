from __future__ import annotations

from datetime import date
from typing import Self

from chess.models.model import Model


class Player(Model):

    def __init__(self,
                 model_id=-1,
                 first_name="",
                 last_name="",
                 birthdate: date | None = None,
                 gender="",
                 rank=-1) -> None:
        super().__init__(model_id)
        self.first_name = first_name
        self.last_name = last_name
        self.birthdate = birthdate
        self.gender = gender
        self.rank = rank

    def __copy__(self):
        return Player(
            model_id=self.model_id,
            first_name=self.first_name,
            last_name=self.last_name,
            birthdate=self.birthdate,
            gender=self.gender,
            rank=self.rank,
        )

    def update(self, src: Self):
        self.model_id = src.model_id
        self.first_name = src.first_name
        self.last_name = src.last_name
        self.birthdate = src.birthdate
        self.gender = src.gender
        self.rank = src.rank
