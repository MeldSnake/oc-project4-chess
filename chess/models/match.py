from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Self

from tinydb import TinyDB
from tinydb.table import Document

from chess.models.model import Model
from chess.serializers import deserialize_datetime, serialize_datetime

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

    @classmethod
    def getTable(cls, db: TinyDB):
        return db.table("matches")

    @classmethod
    def toDocument(cls, value: Self) -> dict:
        data = {
            'start_time': serialize_datetime(value.start_time,),
            'end_time': serialize_datetime(value.end_time),
            'player1': -1 if value.player1 is None else value.player1.model_id,
            'player2': -1 if value.player2 is None else value.player2.model_id,
            'scores': "%f/%f" % value.scores
        }
        data.update(super().toDocument(value))
        return data

    @classmethod
    def fromDocument(cls, db: TinyDB, document: Document) -> Self:
        return Match(
            match_id=document['id'],
            mapped_round=Round.fromID(db, document['round']),
            start_time=deserialize_datetime(document['start_time'], None),
            end_time=deserialize_datetime(document['end_time'], None),
            scores=tuple(float(x) for x in document['scores'].split('/')),
            player1=Player.fromID(db, document['player1']),
            player2=Player.fromID(db, document['player2']),
        )
