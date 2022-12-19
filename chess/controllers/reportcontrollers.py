from typing import TypeVar, Generic
from chess.controllers.controller import Controller, MainStateReturn
from chess.controllers.mainstate import MainViewState
from chess.controllers.menueditcontrollers import ItemSelectionController

from chess.models.player import Player
from chess.models.round import Round
from chess.models.tournament import Tournament
from chess.models.match import Match
from chess.view.reportviews import MatchLongReportView, PlayerReportView, RoundLongReportView, TournamentLongReportView
from chess.view.view import View

T = TypeVar('T', Player, Tournament, Round, Match)


class ReportItemsController(Generic[T], Controller):
    def __init__(self, *items: T) -> None:
        super().__init__()
        self._items = list(items)
        self.view = Player
        self.title = ""
        self.show_header = True

    def item_view_factory(self, idx: int, item: T) -> View:
        raise NotImplementedError()

    def run(self) -> MainStateReturn:
        if self.title != "":
            print("+", "-" * len(self.title), "+", sep='-')
            print("+", self.title, "+")
            print("+", "-" * len(self.title), "+", sep='-')
        for idx, item in enumerate(self._items):
            view = self.item_view_factory(idx, item)
            view.render()
        return MainViewState.BACK, []


class ReportPlayersController(ReportItemsController[Player]):
    def item_view_factory(self, idx: int, item: Player):
        return PlayerReportView(
            last_name=item.last_name,
            first_name=item.first_name,
            birthdate=item.birthdate,
            gender=item.gender,
            rank=item.rank,
        )


class ReportsMatchsController(ReportItemsController[Match]):

    @classmethod
    def get_player_repr(cls, player: Player | None):
        if player is not None:
            return f"{player.first_name} {player.last_name} @{player.rank}"
        return "Auncun Joueur"

    @classmethod
    def get_winner_idx(cls, p1: Player | None, p2: Player | None, winner: Player | None):
        if winner == p1:
            return 0
        elif winner == p2:
            return 1
        return -1

    def item_view_factory(self, idx: int, item: Match) -> View:
        return MatchLongReportView(
            start_time=item.start_time,
            end_time=item.end_time,
            scores=item.scores,
            player1=ReportsMatchsController.get_player_repr(item.player1),
            player2=ReportsMatchsController.get_player_repr(item.player2),
            winner=ReportsMatchsController.get_winner_idx(item.player1, item.player2, item.winner)
        )


class ReportTournamentsController(ItemSelectionController[Tournament]):
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
