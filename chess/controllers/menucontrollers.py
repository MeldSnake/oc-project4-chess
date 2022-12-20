from chess.controllers.controller import MainStateReturn
from chess.controllers.mainstate import MainViewState
from chess.controllers.menueditcontrollers import ItemSelectionController


MenuController = ItemSelectionController[str]


class MainMenuController(MenuController):
    def __init__(self):
        super().__init__(
            "Table des Joueurs",
            "Table des Tournois",
            "Raports",
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
        return super().handle_input(value)


class PlayersMenuController(MenuController):
    def __init__(self):
        super().__init__(
            "Nouveau Joueur",
            "Modifier Joueur",
        )
        self.view.title = "Menu de Gestion des Joueurs"
        self.view.exitName = "Retour"

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

    def handle_input(self, value: int) -> MainStateReturn:
        if value == 0:
            return MainViewState.NEW_TOURNAMENT, []
        elif value == 1:
            return MainViewState.EDIT_TOURNAMENT_MENU, []
        elif value == 2:
            return MainViewState.CONTINUE_TOURNAMENT_MENU, []
        return super().handle_input(value)


class ContinueTournamentController(MenuController):
    def __init__(self):
        super().__init__()
        self.view.exitName = "Retour"
        self.is_tournament_finished = False

    def run(self) -> MainStateReturn:
        if self.is_tournament_finished:
            self.update_choices(
                "Terminer la Ronde en cour"
            )
        else:
            self.update_choices()
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
            return MainViewState.REPORTS_PLAYERS, []
        elif value == 1:
            self.order = "ranking"
            return MainViewState.REPORTS_PLAYERS, []
        elif value == 2:
            self.order = ""
            return MainViewState.REPORTS_TOURNAMENTS_MENU, []
        return super().handle_input(value)
