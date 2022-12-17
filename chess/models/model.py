from __future__ import annotations

from typing import Generator, Self
from weakref import ref

from tinydb import TinyDB, where
from tinydb.queries import QueryInstance, QueryLike
from tinydb.table import Document, Table


class Model:

    @property
    def model_id(self):
        return self.__model_id

    @model_id.setter
    def model_id(self, value: int):
        if value != self.__model_id:
            self.__model_id = value
            self.updated = True

    @property
    def updated(self):
        return self.model_id == -1 or self.__updated

    @updated.setter
    def updated(self, updated: bool):
        self.__updated = updated

    def __init__(self, model_id: int) -> None:
        self.__model_id = model_id
        self.updated = model_id == -1

    def __new__(cls: type[Self], *args, **kwargs) -> Self:
        if not hasattr(cls, "_references"):
            cls._references: list[ref[Self]] = []
        obj = super(Model, cls).__new__(cls)
        cls._references.append(ref(obj))
        return obj

    def copy(self) -> Self:
        raise NotImplementedError()

    def update(self, src: Self):
        raise NotImplementedError()

    @classmethod
    def toDocument(cls, value: Self) -> dict:
        return {
            'id': value.model_id
        }

    @classmethod
    def getTable(cls, db: TinyDB) -> Table:
        raise NotImplementedError()

    @classmethod
    def fromDocument(cls, db: TinyDB, document: Document) -> Self:
        raise NotImplementedError()

    @classmethod
    def _cleaned_references(cls) -> list[ref[Self]]:
        idx = 0
        if not hasattr(cls, '_references'):
            cls._references = []
        while idx < len(cls._references):
            if cls._references[idx]() is None:
                cls._references.pop(idx)
            else:
                idx = idx + 1
        return cls._references

    @classmethod
    def fromID(cls, db: TinyDB, model_id: int) -> Self | None:
        if model_id == -1:
            return None
        for reference in cls._cleaned_references():
            if (unreferenced := reference()) is not None and unreferenced.model_id == model_id:
                return unreferenced
        table = cls.getTable(db)
        if (document := table.get(where("id") == model_id)) is not None:  # type: ignore
            return cls.fromDocument(db, document)
        return None

    @classmethod
    def search(cls, db: TinyDB, query: QueryLike | QueryInstance) -> Generator[Self, None, None]:
        table = cls.getTable(db)
        refs = [x() for x in cls._cleaned_references()]
        for document in table.search(query):  # type: ignore
            found: Self | None = None
            for ref_ in refs:
                if ref_ is not None and ref_.model_id == document['id']:
                    found = ref_
                    break
            if found is None:
                yield cls.fromDocument(db, document)
            else:
                yield found

    @classmethod
    def all(cls, db: TinyDB) -> list[Self]:
        alls = []
        refs = [x() for x in cls._cleaned_references()]
        for document in cls.getTable(db).all():
            found = None
            for ref_ in refs:
                if ref_ is not None and ref_.model_id == document['id']:
                    found = ref_
                    break
            if found is None:
                alls.append(cls.fromDocument(db, document))
            else:
                alls.append(found)
        return alls

    @classmethod
    def save(cls, db: TinyDB, *values: Self):
        ids: list[int] = []
        table = cls.getTable(db)
        for value in values:
            if value.updated:
                if value.model_id == -1:
                    value.model_id = table.insert(cls.toDocument(value))
                else:
                    table.update(cls.toDocument(value), where("id" == value.model_id))  # type: ignore
                value.updated = True
            ids.append(value.model_id)
        return ids
