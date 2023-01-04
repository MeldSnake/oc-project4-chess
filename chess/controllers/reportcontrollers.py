from chess.controllers.mainstate import MainViewState
from chess.controllers.menueditcontrollers import ItemSelectionController
from chess.models.match import Match
from chess.models.player import Player
from chess.models.round import Round
from chess.models.tournament import Tournament
from chess.view.reportviews import (MatchLongReportView, PlayerReportView,
                                    RoundLongReportView,
                                    TournamentLongReportView)
from chess.view.view import View


class ReportPlayersController(ItemSelectionController[Player]):
    def __init__(self, *items: Player) -> None:
        super().__init__(*items)
        self.view.title = "Raports des Joueurs"
        self.view.can_save = False
        self.view.can_repeat_list = False
        self.view.empty_text = "Auncun Joueur Disponible"

    def item_view_factory(self, item: Player, idx: int):
        return PlayerReportView(
            last_name=item.last_name,
            first_name=item.first_name,
            birthdate=item.birthdate,
            gender=item.gender,
            rank=item.rank,
        )


class ReportsMatchsController(ItemSelectionController[Match]):
    def __init__(self, *items: Match) -> None:
        super().__init__(*items)
        self.view.title = "Raports des Matchs"
        self.view.can_save = False
        self.view.can_repeat_list = False
        self.view.empty_text = "Auncun Match Disponible"

    @classmethod
    def get_player_repr(cls, player: Player | None):
        if player is not None:
            return f"{player.first_name} {player.last_name} @{player.rank}"
        return "Auncun Joueur"

    def item_view_factory(self, item: Match, idx: int) -> View:
        return MatchLongReportView(
            scores=item.scores,
            player1=ReportsMatchsController.get_player_repr(item.player1),
            player2=ReportsMatchsController.get_player_repr(item.player2),
        )


class ReportTournamentsController(ItemSelectionController[Tournament]):
    def __init__(self, *items: Tournament) -> None:
        super().__init__(*items)
        self.title = "Raports des Tournois"
        self.view.can_save = False
        self.view.can_repeat_list = False
        self.view.empty_text = "Auncun Tournoi Disponible"
        self.select_state = MainViewState.REPORTS_ROUNDS_MENU

    def item_view_factory(self, item: Tournament, idx: int):
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
            "Raport des Joueurs du Tournoi (score)",
        )
        self.title = "Raports des Rondes"
        self.view.can_save = False
        self.view.can_repeat_list = False
        self.view.empty_text = "Auncune Ronde Disponible"

    def handle_input(self, value: int):
        if value == len(self._items) - 3:
            return MainViewState.REPORTS_ALPHA_PLAYERS, []
        if value == len(self._items) - 2:
            return MainViewState.REPORTS_RANK_PLAYERS, []
        if value == len(self._items) - 1:
            return MainViewState.REPORTS_SCORE_PLAYERS, []
        return super().handle_input(value)

    def item_view_factory(self, item: Round | str, idx: int):
        if isinstance(item, str):
            return item
        return RoundLongReportView(
            index=idx,
            name=item.name,
            number=item.number,
            start_time=item.start_time,
            end_time=item.end_time,
        )
