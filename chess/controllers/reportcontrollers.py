from typing import Generic, TypeVar

from chess.controllers.controller import Controller, MainStateReturn
from chess.controllers.mainstate import MainViewState
from chess.controllers.menueditcontrollers import ItemSelectionController
from chess.models.match import Match
from chess.models.player import Player
from chess.models.round import Round
from chess.models.tournament import Tournament
from chess.view.reportviews import (MatchLongReportView, PlayerReportView,
                                    ReportItemsView, RoundLongReportView,
                                    TournamentLongReportView)
from chess.view.view import View

T = TypeVar('T', Player, Tournament, Round, Match)


class ReportItemsController(Generic[T], Controller):
    def __init__(self, *items: T) -> None:
        super().__init__()
        self._items = list(items)
        self.view = ReportItemsView()
        self.title = ""
        self.show_header = True

    def item_view_factory(self, idx: int, item: T) -> View:
        raise NotImplementedError()

    def _generate_view_map(self):
        for idx, item in enumerate(self._items):
            view = self.item_view_factory(idx, item)
            yield view

    def run(self) -> MainStateReturn:
        self.view.itemViews = self._generate_view_map()
        self.view.render()
        return MainViewState.BACK, []


class ReportPlayersController(ReportItemsController[Player]):
    def __init__(self, *items: Player) -> None:
        super().__init__(*items)
        self.title = "Raports des Joueurs"

    def item_view_factory(self, idx: int, item: Player):
        return PlayerReportView(
            last_name=item.last_name,
            first_name=item.first_name,
            birthdate=item.birthdate,
            gender=item.gender,
            rank=item.rank,
        )


class ReportsMatchsController(ReportItemsController[Match]):
    def __init__(self, *items: Match) -> None:
        super().__init__(*items)
        self.title = "Raports des Matchs"

    @classmethod
    def get_player_repr(cls, player: Player | None):
        if player is not None:
            return f"{player.first_name} {player.last_name} @{player.rank}"
        return "Auncun Joueur"

    def item_view_factory(self, idx: int, item: Match) -> View:
        return MatchLongReportView(
            start_time=item.start_time,
            end_time=item.end_time,
            scores=item.scores,
            player1=ReportsMatchsController.get_player_repr(item.player1),
            player2=ReportsMatchsController.get_player_repr(item.player2),
        )


class ReportTournamentsController(ItemSelectionController[Tournament]):
    def __init__(self, *items: Tournament) -> None:
        super().__init__(*items)
        self.title = "Raports des Tournois"

    def itemViewFactory(self, idx: int, item: Tournament):
        return TournamentLongReportView(
            index=idx,
            name=item.name,
            where=item.where,
            when=item.when,
            style=item.style,
            finished=item.finished,
        )


class ReportRoundsController(ItemSelectionController[Round | str]):
    def __init__(self, /, *choices: Round):
        super().__init__(
            *choices,
            "Raport des Joueurs du Tournoi (abc)",
            "Raport des Joueurs du Tournoi (num)",
        )
        self.title = "Raports des Rondes"

    def handle_input(self, value: int):
        if value == len(self._items):
            return MainViewState.REPORTS_PLAYERS, []
        if value == len(self._items) + 1:
            return MainViewState.REPORTS_PLAYERS, []
        return super().handle_input(value)

    def itemViewFactory(self, item: Round | str, idx: int):
        if isinstance(item, str):
            return item
        return RoundLongReportView(
            index=idx,
            name=item.name,
            number=item.number,
        )
