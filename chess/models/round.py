from __future__ import annotations

from typing import TYPE_CHECKING, Self

from chess.models.model import Model
from datetime import datetime

if TYPE_CHECKING:
    from chess.models.tournament import Tournament
    from chess.models.match import Match
    from chess.models.match import Player


class Round(Model):

    @property
    def scores(self):
        players: dict[Player, float] = {}
        for match in self.matchs:
            if match.player1 is not None:
                players[match.player1] = match.player_score(match.player1)
            if match.player2 is not None:
                players[match.player2] = match.player_score(match.player2)
        return players

    @property
    def finished(self):
        return self.end_time != datetime.min

    def __init__(self,
                 model_id: int = -1,
                 name="",
                 number=-1,
                 tournament: Tournament | None = None,
                 start_time: datetime | None = None,
                 end_time: datetime | None = None,
                 matchs: list[Match] = []) -> None:
        super().__init__(model_id)
        self.name = name
        self.number = number
        self.tournament = tournament
        self.start_time = start_time or datetime.min
        self.end_time = end_time or datetime.min
        self.matchs: list[Match] = list(matchs)

    def __copy__(self):
        return Round(
            model_id=self.model_id,
            name=self.name,
            number=self.number,
            tournament=self.tournament,
            matchs=self.matchs,
        )

    def update(self, src: Self):
        self.model_id = src.model_id
        self.name = src.name
        self.number = src.number
        self.tournament = src.tournament
        self.matchs = src.matchs
