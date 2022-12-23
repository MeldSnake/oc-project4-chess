from __future__ import annotations

from typing import Self


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

    def update(self, src: Self):
        raise NotImplementedError()
