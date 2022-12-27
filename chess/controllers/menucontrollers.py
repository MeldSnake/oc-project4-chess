from chess.algorithm import SwissSystem
from chess.controllers.controller import Controller, MainStateReturn
from chess.controllers.mainstate import MainViewState
from chess.controllers.menueditcontrollers import ItemSelectionController
from chess.models.player import Player
from chess.models.tournament import Tournament
import chess.controllers.reportcontrollers as rc
import chess.view.reportviews as rv
from chess.view.view import View


MenuController = ItemSelectionController[str]


class MainMenuController(MenuController):
    def __init__(self):
        super().__init__(
            "Table des Joueurs",
            "Table des Tournois",
            "Raports",
            "Continuer un tournoi",
        )
        self.view.title = "Menu Principal"
        self.view.show_header = True
        self.quit_state = MainViewState.QUIT

    def handle_input(self, value: int) -> MainStateReturn:
        if value == 0:
            self.view.show_header = True
            return MainViewState.PLAYERS_MENU, []
        elif value == 1:
            self.view.show_header = True
            return MainViewState.TOURNAMENTS_MENU, []
        elif value == 2:
            self.view.show_header = True
            return MainViewState.REPORTS_MENU, []
        elif value == 3:
            self.view.show_header = True
            return MainViewState.CONTINUE_TOURNAMENT_MENU, []
        return super().handle_input(value)


class PlayersMenuController(MenuController):
    def __init__(self):
        super().__init__(
            "Nouveau Joueur",
            "Modifier Joueur",
        )
        self.view.title = "Menu de Gestion des Joueurs"
        self.view.exitName = "Retour"

    def onSave(self):
        self.view.show_header = False

    def handle_input(self, value: int) -> MainStateReturn:
        if value == 0:
            return MainViewState.NEW_PLAYER, []
        elif value == 1:
            return MainViewState.EDIT_PLAYER_MENU, []
        return super().handle_input(value)


class TournamentsMenuController(MenuController):
    def __init__(self):
        super().__init__(
            "Nouveau Tournoi",
            "Modifier un Tournoi",
            "Continuer un Tournoi",
        )
        self.view.title = "Menu de Gestion des Tournois"
        self.view.exitName = "Retour"

    def onSave(self):
        self.view.show_header = False

    def handle_input(self, value: int) -> MainStateReturn:
        self.view.show_header = True
        if value == 0:
            return MainViewState.NEW_TOURNAMENT, []
        elif value == 1:
            return MainViewState.EDIT_TOURNAMENT_MENU, []
        elif value == 2:
            return MainViewState.CONTINUE_TOURNAMENT_MENU, []
        return super().handle_input(value)


class ContinueFinishedTournamentController(MenuController):
    def __init__(self, system: SwissSystem):
        super().__init__()
        self.system = system

    def run(self) -> MainStateReturn:
        View.render_title("Tournois Terminé")
        rv.TournamentReportView(
            name=self.system.tournament.name,
            where=self.system.tournament.where,
            round_count=self.system.tournament.round_count,
            round_completed=len([x for x in self.system.tournament.rounds if x.finished]),
            when=self.system.tournament.when,
            style=self.system.tournament.style,
            finished=self.system.tournament.finished,
        ).render()
        View.render_title("Vainqueur")
        winner = self.system.tournament.winner
        rv.PlayerReportView(
            last_name=winner.last_name,
            first_name=winner.first_name,
            birthdate=winner.birthdate,
            gender=winner.gender,
            rank=winner.rank,
        ).render()
        return super().run()


class ContinueStartedRoundController(MenuController):
    def __init__(self, system: SwissSystem):
        super().__init__(
            "Terminer la ronde en cours",
        )
        self.system = system

    def handle_input(self, value: int):
        if value == 0:
            return MainViewState.CONTINUE_END_ROUND, []
        return super().handle_input(value)

    def run(self) -> MainStateReturn:
        return super().run()


class ContinueFinishedRoundController(MenuController):
    def __init__(self, system: SwissSystem):
        super().__init__(
            "Demarrer la ronde suivante",
        )
        self.system = system
        self.reports_controller = rc.ReportsMatchsController()

    def handle_input(self, value: int):
        if value == 0:
            return MainViewState.CONTINUE_START_ROUND, []
        return super().handle_input(value)

    def run(self) -> MainStateReturn:
        self.reports_controller.update_items(*self.system.tournament.rounds[-1].matchs)
        self.reports_controller.run()
        return super().run()


class ContinueInitTournamentController(Controller):
    def __init__(self, tournament: Tournament):
        super().__init__()
        self._menu_view = MenuController(
            "Ajouter un joueur",
            "Demarrer le tournoi",
        )
        self.tournament = tournament
        self.err_str: str | None = None

    def run(self) -> MainStateReturn:
        if self.err_str is not None:
            print(self.err_str)
            self.err_str = None
            return None, None
        else:
            state, _ = self._menu_view.run()
            if self._menu_view.selected_index == 0:
                return MainViewState.SELECT_PLAYER, []
            elif self._menu_view.selected_index == 1:
                return MainViewState.CONTINUE_STARTED_ROUND, []
            return (state or MainViewState.BACK), []
        return None, None


class WinnerChooserController(ItemSelectionController[Player | str | None]):
    @property
    def winner(self):
        selected = self.selected_item
        if isinstance(selected, Player):
            return selected
        return None

    @property
    def equality(self):
        return self.selected_index == 2

    def __init__(self, player1: Player | None, player2: Player | None):
        super().__init__(
            player1,
            player2,
            "Egalité",
        )
        self.view.title = "Selection du vainqueur du match"
        self.view.can_save = False
        self.view.can_repeat_list = False

    def itemViewFactory(self, value: Player | None, idx: int) -> str | View | None:
        if isinstance(value, (str, int, float)):
            return str(value)
        if value is None:
            return None
        return rv.PlayerReportView(
            index=idx,
            first_name=value.first_name,
            last_name=value.last_name,
            birthdate=value.birthdate,
            gender=value.gender,
            rank=value.rank,
        )

    def run(self) -> MainStateReturn:
        if any([x is None for x in self._items[:2]]):
            return MainViewState.BACK, []
        return super().run()


class ReportsMenuController(MenuController):
    def __init__(self, /):
        super().__init__(
            "Raport des Joueurs par ordre alphabetic",
            "Raport des Joueurs par classement",
            "Raport des Tournois",
        )
        self.view.title = "Menu des Raports"
        self.view.exitName = "Retour"
        self.order = "alphabetic"
        self.view.can_save = False

    def handle_input(self, value: int):
        if value == 0:
            self.order = "alphabetic"
            return MainViewState.REPORTS_ALPHA_PLAYERS, []
        elif value == 1:
            self.order = "ranking"
            return MainViewState.REPORTS_RANK_PLAYERS, []
        elif value == 2:
            self.order = ""
            return MainViewState.REPORTS_TOURNAMENTS_MENU, []
        return super().handle_input(value)
