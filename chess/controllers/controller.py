from typing import Any
from chess.controllers.mainstate import MainViewState


MainStateReturn = tuple[None, None] | tuple[MainViewState, list[Any]]


class Controller:
    def feedArguments(self, *args):
        pass

    def run(self) -> MainStateReturn:
        raise NotImplementedError()
