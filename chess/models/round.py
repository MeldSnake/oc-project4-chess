from __future__ import annotations

from typing import TYPE_CHECKING, Self

from chess.models.model import Model

if TYPE_CHECKING:
    from chess.models.tournament import Tournament


class Round(Model):

    def __init__(self,
                 model_id: int = -1,
                 name="",
                 number=-1,
                 tournament: Tournament | None = None) -> None:
        super().__init__(model_id)
        self.name = name
        self.number = number
        self.tournament = tournament

    def __copy__(self):
        return Round(
            model_id=self.model_id,
            name=self.name,
            number=self.number,
            tournament=self.tournament,
        )

    def update(self, src: Self):
        self.model_id = src.model_id
        self.name = src.name
        self.number = src.number
        self.tournament = src.tournament
