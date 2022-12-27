from datetime import date, time
from typing import Any, Generic, NamedTuple, Type, TypeVar, overload
from chess.controllers.controller import Controller, MainStateReturn
from chess.controllers.mainstate import MainViewState
from chess.models.match import Match
from chess.models.player import Player
from chess.models.round import Round
from chess.models.tournament import Tournament
from chess.view.menuview import MenuItemsView
from chess.view.reportviews import MatchReportView, PlayerReportView, RoundReportView, TournamentReportView
from chess.view.textview import TextView
from chess.view.view import View

T = TypeVar('T')


class ItemSelectionController(Controller, Generic[T]):
    @property
    def selected_item(self):
        if self.selected_index >= 0 and self.selected_index < len(self._items):
            return self._items[self.selected_index]
        return None

    def __init__(self, /, *choices: T):
        self._items: list[T] = list(choices)
        self.view = MenuItemsView()
        self.update_choices(*choices)
        self.invalid_view = TextView()
        self.is_invalid_input = False
        self.quit_state = MainViewState.BACK
        self.select_state = MainViewState.BACK
        self.selected_index = -1

    def __del__(self):
        self.onQuit()

    def update_choices(self, /, *choices: T):
        self.selected_index = -1
        self._items = list(choices)
        self.view.choices = list(
            filter(
                lambda x: x is not None,
                map(self.itemViewFactory, self._items, range(0, len(self._items)))
            )
        )  # type: ignore

    def handle_input(self, value: int):
        if value >= 0 and value < len(self._items):
            self.selected_index = value
            return self.select_state, []
        else:
            self.selected_index = -1
            self.is_invalid_input = True
            self.view.show_header = False
            self.invalid_view.text = "Option non reconnue, réessayé"
        return None, None

    @overload
    def itemViewFactory(self, value: str | int | float, idx: int) -> str | None: ...
    @overload
    def itemViewFactory(self, value: Any, idx: int) -> View | None: ...

    def itemViewFactory(self, value: T, idx: int) -> str | View | None:
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
        else:
            self.invalid_view.text = "Option non reconnue, réessayé"
            self.view.show_header = False
        return None, None


class PlayerSelectionController(ItemSelectionController[Player]):
    def itemViewFactory(self, value: Player | str, idx: int) -> str | View:
        if isinstance(value, (str, int, float)):
            return str(value)
        return PlayerReportView(
            index=idx,
            last_name=value.last_name,
            first_name=value.first_name,
            birthdate=value.birthdate,
            gender=value.gender,
            rank=value.rank,
        )


class TournamentSelectionController(ItemSelectionController[Tournament]):
    def __init__(self, *tournaments: Tournament):
        super().__init__(*tournaments)
        self.view.title = "Selection de tournoi"
        self.view.exitName = "Retour"
        self.view.can_repeat_list = False
        self.view.can_save = False

    def itemViewFactory(self, value: Tournament | str, idx: int) -> str | View:
        if isinstance(value, (str, int, float)):
            return str(value)
        return TournamentReportView(
            index=idx,
            finished=value.finished,
            name=value.name,
            round_completed=len([x for x in value.rounds if x.finished]),
            round_count=value.round_count,
            style=value.style,
            when=value.when,
            where=value.where,
        )


class RoundSelectionController(ItemSelectionController[Round]):
    def __init__(self, *rounds: Round):
        super().__init__(*rounds)
        self.view.title = "Selection de ronde"
        self.view.exitName = "Retour"
        self.view.can_repeat_list = False
        self.view.can_save = False

    def itemViewFactory(self, value: Round | str, idx: int) -> str | View:
        if isinstance(value, (str, int, float)):
            return str(value)
        return RoundReportView(
            index=idx,
            name=value.name,
            number=value.number,
        )


class MatchSelectionController(ItemSelectionController[Match]):
    def __init__(self, *matchs: Match):
        super().__init__(*matchs)
        self.view.title = "Selection de match"
        self.view.exitName = "Retour"
        self.view.can_repeat_list = False
        self.view.can_save = False

    def itemViewFactory(self, value: Match | str, idx: int) -> str | View:
        if isinstance(value, (str, int, float)):
            return str(value)
        return MatchReportView(
            index=idx,
            start_time=value.start_time,
            end_time=value.end_time,
            scores=value.scores,
        )


class EditPlayerMenuController(ItemSelectionController[Player]):
    def __init__(self, /, *choices: Player):
        super().__init__(*choices)
        self.view.can_repeat_list = False
        self.view.exitName = "Retour"
        self.view.title = "Selection du Joueur"
        self.view.can_save = True
        self.select_state = MainViewState.EDIT_PLAYER

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


class EditTournamentMenuController(ItemSelectionController[Tournament | str]):
    def __init__(self, /, *choices: Tournament):
        super().__init__(
            *choices,
        )
        self.view.can_repeat_list = True
        self.view.exitName = "Retour"
        self.view.title = "Selection du Tournoi"
        self.view.can_save = False
        self.select_state = MainViewState.EDIT_TOURNAMENT

    def itemViewFactory(self, tournament: Tournament | str, idx: int):
        if isinstance(tournament, str):
            return tournament
        return TournamentReportView(
            index=idx,
            name=tournament.name,
            when=tournament.when,
            where=tournament.where,
            style=tournament.style,
            finished=tournament.finished,
        )

    def run(self) -> MainStateReturn:
        if len(self._items) == 0:
            self.view.err_str = "\r\nPas de tournoi existant\r\n"
        return super().run()


class EditRoundMenuController(ItemSelectionController[Round | str]):
    def __init__(self, /, *choices: Round):
        super().__init__(*choices)
        self.view.can_repeat_list = True
        self.view.exitName = "Retour"
        self.view.title = "Selection d'une Ronde"
        self.view.can_save = False
        self.select_state = MainViewState.EDIT_ROUND

    def itemViewFactory(self, round_: Round | str, idx: int):
        if isinstance(round_, str):
            return round_
        # TODO Reach implementation
        return RoundReportView(
            index=idx,
            name=round_.name,
            number=round_.number,
        )

    def run(self) -> MainStateReturn:
        if len(self._items) == 0:
            self.view.err_str = "\r\nPas de round existant\r\n"
        return super().run()


class EditMatchMenuController(ItemSelectionController[Match | str]):
    def __init__(self, /, *choices: Match):
        super().__init__(
            *choices,
        )
        self.view.can_repeat_list = True
        self.view.exitName = "Retour"
        self.view.title = "Selection d'un Match"
        self.view.can_save = False
        self.select_state = MainViewState.EDIT_MATCH

    def itemViewFactory(self, match: Match | str, idx: int):
        if isinstance(match, str):
            return match
        # TODO Reach implementation
        return MatchReportView(
            index=idx,
            start_time=match.start_time,
            end_time=match.end_time,
            scores=match.scores,
        )

    def run(self) -> MainStateReturn:
        if len(self._items) == 0:
            self.view.err_str = "\r\nPas de match existant\r\n"
        return super().run()


class ContinueTournamentMenuController(EditTournamentMenuController):
    def __init__(self, /, *choices: Tournament):
        super().__init__(*choices)
        self.select_state = MainViewState.CONTINUE_TOURNAMENT


class EditField(NamedTuple):
    name: str
    vtype: Type[Any] | None
    field_name: str | None


class OutStateField(NamedTuple):
    name: str
    state: MainViewState


class EditController(ItemSelectionController[str]):
    def __init__(self, *edit_fields: EditField | OutStateField):
        super().__init__(
            *map(lambda x: x.name, edit_fields),
            "Confirmer les modifications",
        )
        self.edit_fields = list(edit_fields)
        self.view.exitName = "Annuler"
        self.field_edit: str | None = None
        self.vtype = type(None)

    def handle_input(self, value: int):
        if value >= 0:
            if value < len(self.edit_fields):
                field = self.edit_fields[value]
                if isinstance(field, EditField):
                    self.field_edit = field.field_name
                    self.vtype = field.vtype
                    return MainViewState.EDIT_FIELD, []
                else:
                    self.field_edit = None
                    self.vtype = None
                    return field.state, []
            elif value == len(self.edit_fields):
                return MainViewState.SAVE_ITEM, []
        return super().handle_input(value)


class EditPlayerController(EditController):
    def __init__(self):
        super().__init__(
            EditField("Definir le prenom", str, "first_name"),
            EditField("Definir le nom de famille", str, "last_name"),
            EditField("Definir la date de naissance", date, "birthdate"),
            EditField("Definir le genre", str, "gender"),
            EditField("Definir le classement", int, "rank"),
        )
        self.view.title = "Modification du Joueur"


class EditTournamentController(EditController):
    def __init__(self):
        super().__init__(
            EditField("Definir le nom", str, "name"),
            EditField("Definir le lieu", str, "where"),
            EditField("Definir la date", date, "when"),
            OutStateField("Definir le style", MainViewState.EDIT_TOURNAMENT_STYLE),
            OutStateField("Modifier une ronde du Tournoi", MainViewState.EDIT_ROUND_MENU),
            OutStateField("Demarrer/Continuer ce tournoi", MainViewState.CONTINUE_TOURNAMENT),
        )
        self.view.title = "Modification du Tournoi"

    def handle_input(self, value: int):
        return super().handle_input(value)


class EditRoundController(EditController):
    def __init__(self):
        super().__init__(
            EditField("Definir le nom", str, "name"),
            OutStateField("Modifier un match de la ronde", MainViewState.EDIT_MATCH_MENU),
        )
        self.view.title = "Modification de la Ronde"


class EditMatchController(EditController):
    def __init__(self):
        super().__init__(
            EditField("Definir l'heure de debut", time, "start_time"),
            EditField("Definir l'heure de fin", time, "end_time"),
            OutStateField("Definir les scores", MainViewState.SET_MATCH_SCORE),
            OutStateField("Definir le vainqueur", MainViewState.CHOOSE_MATCH_WINNER),
        )
        self.view.title = "Modification du Match"
