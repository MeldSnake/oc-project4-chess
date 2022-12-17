from datetime import date
from typing import Any, Generic, TypeVar, overload

from chess.controllers.controller import Controller, MainStateReturn
from chess.controllers.mainstate import MainViewState
from chess.models.player import Player
from chess.models.tournament import Tournament
from chess.view.menuview import MenuItemsView, PlayerReportView
from chess.view.textview import TextView
from chess.view.view import View


T = TypeVar('T')


class MenuItemsController(Controller, Generic[T]):
    def __init__(self, /, *choices: T):
        self._items: list[T] = list(choices)
        self.view = MenuItemsView()
        self.update_choices(*choices)
        self.invalid_view = TextView()
        self.is_invalid_input = False
        self.quit_state = MainViewState.BACK

    def __del__(self):
        self.onQuit()

    def update_choices(self, /, *choices: T):
        self._items = list(choices)
        self.view.choices = list(map(self.itemViewFactory, self._items, range(0, len(self._items))))

    def handle_input(self, value: int):
        self.is_invalid_input = True
        self.invalid_view.text = "Valeur invalide, réessayé"
        return None, None

    @overload
    def itemViewFactory(self, value: str | int | float, idx: int) -> str: ...
    @overload
    def itemViewFactory(self, value: Any, idx: int) -> View: ...

    def itemViewFactory(self, value: T, idx: int) -> str | View:
        if isinstance(value, (str, int, float)):
            return str(value)
        raise NotImplementedError("itemViewFactory not properly implemented for MenuItemController subclass")

    def onSave(self):
        pass

    def onQuit(self):
        pass

    def onView(self):
        pass

    def run(self) -> MainStateReturn:
        if self.is_invalid_input:
            self.invalid_view.render()
            self.invalid_view.text = ""
            self.is_invalid_input = False
            return None, None
        user_input = self.view.render()
        self.view.show_header = False
        if user_input is None:
            return MainViewState.BACK, []
        elif user_input.isdigit():
            value = int(user_input)
            return self.handle_input(value)
        elif user_input == "s" and self.view.can_save:
            self.onSave()
            return MainViewState.SAVE_DATABASE, []
        elif user_input == "?" and self.view.can_repeat_list:
            self.onView()
            self.view.show_header = True
        elif user_input == "q":
            self.onQuit()
            self.view.choices = []
            self._items = []
            return self.quit_state, []
        return None, None


MenuController = MenuItemsController[str]


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


# NewPlayer is an action
class EditPlayerMenuController(MenuItemsController[Player]):
    def __init__(self, /, *choices: Player):
        super().__init__(*choices)
        self.view.can_repeat_list = False
        self.view.exitName = "Retour"
        self.selected_player: Player | None = None

    def itemViewFactory(self, player: Player, idx: int) -> View:
        return PlayerReportView(
            index=idx,
            last_name=player.last_name,
            first_name=player.first_name,
            birthdate=player.birthdate,
            gender=player.gender,
            rank=player.rank,
        )

    def run(self) -> MainStateReturn:
        if len(self._items) == 0:
            self.view.err_str = "\r\nPas de joueur existant\r\n"
        return super().run()

    def handle_input(self, value: int) -> MainStateReturn:
        if value >= 0 and value <= len(self._items):
            self.selected_player = self._items[value]
            self.onQuit()
            return MainViewState.EDIT_PLAYER, []
        return super().handle_input(value)


class EditPlayerController(MenuController):
    def __init__(self):
        super().__init__(
            "Definir le prenom",
            "Definir le nom de famille",
            "Definir la date de naissance",
            "Definir le genre",
            "Definir le classement",
            "Confirmer les modifications",
        )
        self.view.exitName = "Annuler"
        self.field_edit: str | None = None
        self.vtype = type(None)

    def handle_input(self, value: int) -> MainStateReturn:
        if value == 0:
            self.field_edit = "last_name"
            self.vtype = str
            return MainViewState.EDIT_FIELD, []
        elif value == 1:
            self.field_edit = "first_name"
            self.vtype = str
            return MainViewState.EDIT_FIELD, []
        elif value == 2:
            self.field_edit = "birthdate"
            self.vtype = date
            return MainViewState.EDIT_FIELD, []
        elif value == 3:
            self.field_edit = "gender"
            self.vtype = str
            return MainViewState.EDIT_FIELD, []
        elif value == 4:
            self.field_edit = "rank"
            self.vtype = int
            return MainViewState.EDIT_FIELD, []
        elif value == 5:
            return MainViewState.SAVE_ITEM, []
        return super().handle_input(value)


class TournamentsMenuController(MenuController):
    def __init__(self):
        super().__init__(
            "Nouveau Tournoi",
            "Modifier un Tournoi",
            "Continuer un Tournoi",
        )
        self.view.exitName = "Retour"

    def handle_input(self, value: int) -> MainStateReturn:
        if value == 0:
            return MainViewState.NEW_TOURNAMENT, []
        elif value == 1:
            return MainViewState.EDIT_TOURNAMENT_MENU, []
        elif value == 2:
            return MainViewState.CONTINUE_TOURNAMENT_MENU, []
        return super().handle_input(value)


# NewTournament is an action
class EditTournamentMenuController(MenuItemsController[Tournament]):
    def __init__(self, /, *choices: Tournament):
        super().__init__(*choices)
        self.view.can_repeat_list = True
        self.view.exitName = "Retour"
        self.selected_tournament: Tournament | None = None

    def run(self) -> MainStateReturn:
        if len(self._items) == 0:
            self.view.err_str = "\r\nPas de tournoi existant\r\n"
        return super().run()

    def handle_input(self, value: int) -> MainStateReturn:
        if value >= 0 and value <= len(self._items):
            item = self._items[value]
            self.selected_tournament = item
            self.onQuit()
            return MainViewState.EDIT_TOURNAMENT, []
        return super().handle_input(value)


class EditTournamentController(MenuController):
    def __init__(self):
        super().__init__()
        self.tournament: Tournament | None = None
        self.view.exitName = "Annuler"
        self.field_edit: str | None = None
        self.vtype = type(None)


class ContinueTournamentMenuController(MenuItemsController[Tournament]):
    def __init__(self, /, *choices: Tournament):
        super().__init__(*choices)
        self.selected_tournament: Tournament | None = None

    def run(self) -> MainStateReturn:
        if len(self._items) == 0:
            self.view.err_str = "\r\nPas de tournoi existant\r\n"
        return super().run()

    def handle_input(self, value: int) -> MainStateReturn:
        if value >= 0 and value <= len(self._items):
            item = self._items[value]
            self.selected_tournament = item
            self.onQuit()
            return MainViewState.CONTINUE_TOURNAMENT, []
        return super().handle_input(value)


class ContinueTournamentController(MenuController):
    def __init__(self):
        super().__init__(
            "Terminaliser le round en cours",
        )
        self.view.exitName = "Retour"
