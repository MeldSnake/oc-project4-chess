from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Self

from chess.models.model import Model

if TYPE_CHECKING:
    from chess.models.player import Player
    from chess.models.round import Round


class Match(Model):

    def __init__(self, /, *,
                 match_id=-1,
                 mapped_round: Round | None = None,
                 start_time: datetime | None = None,
                 end_time: datetime | None = None,
                 scores: tuple[float, float] = (0.0, 0.0),
                 player1: Player | None = None,
                 player2: Player | None = None):
        super().__init__(match_id)
        self.round = mapped_round
        self.start_time = start_time
        self.end_time = end_time
        self.scores = scores
        self.player1 = player1
        self.player2 = player2

    def player_score(self, player: Player):
        if player is self.player1:
            return self.scores[0]
        elif player is self.player2:
            return self.scores[1]
        return 0.0

    def __copy__(self):
        return Match(
            match_id=self.model_id,
            mapped_round=self.round,
            start_time=self.start_time,
            end_time=self.end_time,
            scores=self.scores,
            player1=self.player1,
            player2=self.player2,
        )

    def update(self, src: Self):
        self.match_id = src.model_id
        self.mapped_round = src.round
        self.start_time = src.start_time
        self.end_time = src.end_time
        self.scores = src.scores
        self.player1 = src.player1
        self.player2 = src.player2
