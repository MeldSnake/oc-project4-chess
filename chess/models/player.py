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
                 classement=-1) -> None:
        super().__init__(model_id)
        self.first_name = first_name
        self.last_name = last_name
        self.birthdate = birthdate
        self.gender = gender
        self.classement = classement

    @classmethod
    def getTable(cls, db: TinyDB):
        return db.table("players")

    @classmethod
    def toDocument(cls, value: Self) -> dict:
        data: dict = {
            'first_name': value.first_name,
            'last_name': value.last_name,
            'brithdate': serialize_date(value.birthdate, ""),
            'gender': value.gender,
            'classment': value.classement
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
            classement=document['classement'],
        )
