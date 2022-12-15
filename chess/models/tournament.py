from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Self

from tinydb import TinyDB
from tinydb.table import Document

from chess.models.model import Model
from chess.serializers import serialize_date


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

    @classmethod
    def getTable(cls, db: TinyDB):
        return db.table("tournaments")

    @classmethod
    def toDocument(cls, value: Self):
        data: dict = {
            'name': value.name,
            'where': value.where,
            'when': serialize_date(value.when),
            'style': value.style,
            'finished': value.finished,
        }
        data.update(super().toDocument(value))
        return data

    @classmethod
    def fromDocument(cls, _: TinyDB, document: Document) -> Self:
        return Tournament(
            model_id=document['id'],
            name=document['name'],
            where=document['where'],
            when=document['when'],
            style=document['style'],
            finished=bool(document['finished']),
        )
