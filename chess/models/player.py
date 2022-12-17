from __future__ import annotations

from datetime import date
from typing import Self

from tinydb import TinyDB
from tinydb.table import Document

from chess.models.model import Model
from chess.serializers import deserialize_date, serialize_date


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

    def copy(self):
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

    @classmethod
    def getTable(cls, db: TinyDB):
        return db.table("players")

    @classmethod
    def toDocument(cls, value: Self) -> dict:
        data: dict = {
            'first_name': value.first_name,
            'last_name': value.last_name,
            'birthdate': serialize_date(value.birthdate, ""),
            'gender': value.gender,
            'rank': value.rank
        }
        data.update(super().toDocument(value))
        return data

    @classmethod
    def fromDocument(cls, db: TinyDB, document: Document) -> Self:
        return Player(
            model_id=document['id'],
            first_name=document['first_name'],
            last_name=document['last_name'],
            birthdate=deserialize_date(document['birthdate'], None),
            gender=document['gender'],
            rank=document['rank'],
        )
