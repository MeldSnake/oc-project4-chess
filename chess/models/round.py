from __future__ import annotations

from typing import TYPE_CHECKING, Self

from tinydb import TinyDB
from tinydb.table import Document

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

    @classmethod
    def getTable(cls, db: TinyDB):
        return db.table("rounds")

    @classmethod
    def toDocument(cls, value: Self):
        data: dict = {
            'name': value.name,
            'number': value.number,
            'tid': value.tournament.model_id if value.tournament is not None else -1,
        }
        data.update(super().toDocument(value))
        return data

    @classmethod
    def fromDocument(cls, db: TinyDB, document: Document):
        return Round(
            model_id=document['id'],
            name=document["name"],
            number=document["number"],
            tournament=Tournament.fromID(db, document['tid'])
        )
