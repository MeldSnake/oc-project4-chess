from enum import Enum
from typing import TYPE_CHECKING
from chess.algorithm import SwissSystem
from chess.controllers.editcontrollers import EditController
from chess.controllers.menucontrollers import MenuController
from chess.controllers.menueditcontrollers import PlayerSelectionController

from chess.database.dbadapter import DBAdapter
from chess.controllers.controller import Controller, MainStateReturn, MainViewState
from chess.view.reportviews import PlayerReportView, TournamentReportView
from chess.view.view import View

if TYPE_CHECKING:
    from chess.models.tournament import Tournament


class ContinueControllerState(int, Enum):
    MENU_SELECT = 0
    START_TOURNAMENT = 1
    FINISH_ROUND = 2
    START_ROUND = 3
    QUERY_SCORES = 4


class FinishedTournamentMenuController(MenuController):
    @property
    def tournament(self):
        return self.__tournament

    @tournament.setter
    def tournament(self, tournament: Tournament):
        self.__tournament = tournament
        self._tournament_view = TournamentReportView(
            name=tournament.name,
            where=tournament.where,
            when=tournament.when,
            style=tournament.style,
            finished=tournament.finished,
        )
        winner = tournament.winner
        self._winner_view = PlayerReportView(
            last_name=winner.last_name,
            first_name=winner.first_name,
            birthdate=winner.birthdate,
            gender=winner.gender,
            rank=winner.rank,
        )

    @tournament.deleter
    def tournament(self):
        self.__tournament = None

    def __init__(self, tournament: Tournament):
        super().__init__()
        self.tournament = tournament

    def run(self) -> MainStateReturn:
        if self.view.show_header:
            View.render_title("Tournoi terminé")
            self._tournament_view.render()
            View.render_title("Vainqueur du tournoi")
            self._winner_view.render()
        return super().run()


class StartTournamentController(MenuController):
    def __init__(self, tournament: Tournament):
        super().__init__(
            "Changer le nombre de rondes",
            "Ajouter un joueur existant",
            "Creer un joueur",
        )
        self.tournament = tournament
        self._number_input_view = EditController(int)
        self._select_player = PlayerSelectionController()

    def handle_input(self, value: int):
        if value == 0:
            self._number_input_view.oldValue = self.tournament.round_count
            while True:
                state, _ = self._number_input_view.run()
                if state == MainViewState.BACK:
                    if self._number_input_view.value is not None:
                        self.tournament.round_count = self._number_input_view.value
        elif value == 1:
            self._select_player


class FinishRoundMenuController(MenuController):
    def __init__(self, /, system: SwissSystem):
        super().__init__(
            "Finaliser la ronde en cours",
        )
        self.system = system
        self.finished_round = None
        self.started_round = None

    def handle_input(self, value: int):
        if value == 0:
            self.finished_round = self.system.round
            self.system.next_round()
            return None, None
        return super().handle_input(value)


class ContinueController(Controller):
    def __init__(self, db: DBAdapter, tournament: Tournament) -> None:
        super().__init__()
        self._db = db
        self.tournament_system = SwissSystem(tournament)
        self.state = ContinueControllerState.MENU_SELECT
        self.menu_controller = MenuController()

    def _run_menu_select(self):
        if self.tournament_system.tournament.finished:
            if not isinstance(self.menu_controller, FinishedTournamentMenuController):
                self.menu_controller = FinishedTournamentMenuController(
                    self.tournament_system.tournament
                )
            return self.menu_controller.run()
        else:
            if len(self.tournament_system.tournament.rounds) != 0:
                last_round = self.tournament_system.tournament.rounds[0]
            else:
                last_round = None
            if last_round is not None and last_round.started and not last_round.finished:
                if not isinstance(self.menu_controller, FinishRoundMenuController):
                    self.menu_controller = FinishRoundMenuController(last_round)
                state, _ = self.menu_controller.run()
                if state is None:
                    if self.menu_controller.finished_round:
                        self.state = ContinueControllerState.FINISH_ROUND
                        self.tournament_system.next_round()
            if not isinstance(self.menu_controller, StartTournamentController):
                self.menu_controller = StartTournamentController(self.tournament_system.tournament)
            self.menu_controller.run()
            if not isinstance(self.menu_controller, FinishRoundMenuController):
                self.menu_controller = FinishRoundMenuController(self.tournament_system.tournament)
            self.menu_controller.run()
            if len(self.tournament_system.tournament.rounds) == self.tournament_system.tournament.round_count:
                pass
        return None, None

    def run(self) -> MainStateReturn:
        if self.state == ContinueControllerState.MENU_SELECT:
            return self._run_menu_select()
        elif self.state == ContinueControllerState.START_TOURNAMENT:
            pass
        elif self.state == ContinueControllerState.FINISH_ROUND:
            pass
        elif self.state == ContinueControllerState.START_ROUND:
            pass
        elif self.state == ContinueControllerState.QUERY_SCORES:
            pass
        else:
            self.state = ContinueControllerState.MENU_SELECT
        return None, None
