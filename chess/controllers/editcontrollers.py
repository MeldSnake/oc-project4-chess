from chess.controllers.controller import Controller, MainStateReturn
from typing import Type, TypeVar, Generic
from datetime import date, time, datetime
from chess.controllers.mainstate import MainViewState
from chess.controllers.menueditcontrollers import ItemSelectionController
from chess.models.tournament import StyleTournament
from chess.view.editviews import EditView

T = TypeVar('T', str, int, float, date, time)


class EditController(Generic[T], Controller):
    def __init__(self, vtype: Type[T]) -> None:
        super().__init__()
        self.vtype = vtype
        self.value: T | None = None
        self.oldValue: T | None = None
        self.view = EditView()

    def deserialize_value(self, value: str) -> T | ValueError | None:
        if self.vtype == str:
            return value  # type: ignore
        if self.vtype == int:
            return int(value)  # type: ignore
        if self.vtype == float:
            return float(value)  # type: ignore
        if self.vtype == date:
            try:
                dt = datetime.strptime(value, "%d/%m/%Y")
            except ValueError:
                dt = None
            if dt is None:
                return ValueError()
            return dt.date()  # type: ignore
        if self.vtype == time:
            try:
                dt = datetime.strptime(value, "%H:%M")
            except ValueError:
                dt = None
            if dt is None:
                return ValueError()
            return dt.time()  # type: ignore
        raise TypeError("Type not supported")

    def serialize_value(self, value: T | None):
        if value is None:
            return None
        if isinstance(value, (str, int, float)):
            return str(value)
        if isinstance(value, date):
            return value.strftime("%d/%m/%Y")
        if isinstance(value, time):
            return value.strftime("%H:%M")
        raise ValueError("Type non supporté")

    def run(self) -> MainStateReturn:
        self.view.oldValue = self.serialize_value(self.oldValue)
        value = self.view.render()
        if value == "":
            value = self.oldValue
        else:
            value = self.deserialize_value(value)
        if isinstance(value, ValueError):
            self.view.error = "Valeur invalide, réessayé"
            return None, None
        else:
            self.value = value
        return MainViewState.BACK, []


class EditDatetimeController(Controller):
    @property
    def value(self):
        if self.date is not None and self.time is not None:
            return datetime.combine(self.date, self.time)
        return None

    def __init__(self) -> None:
        super().__init__()
        self.date: date | None = None
        self.time: time | None = None
        self.oldValue: datetime | None = None
        self.state = 0
        self.view_date = EditView()
        self.view_date.pre_header = "Definition de la partie date"
        self.view_time = EditView()
        self.view_time.pre_header = "Definition de la partie heure"

    def run(self) -> MainStateReturn:
        if isinstance(self.oldValue, time):
            self.date = datetime.today()
            self.state = 1
        elif isinstance(self.oldValue, date) and self.state != 0:
            self.state = 0
            self.time = datetime.now().time()
            return MainViewState.BACK, []
        if self.state == 0:
            self.view_date.oldValue = self.oldValue.strftime("%d/%m/%Y") if self.oldValue is not None else None
            value = self.view_date.render()
            if value != "":
                try:
                    value = datetime.strptime(value, "%d/%m/%Y")
                except ValueError:
                    value = None
                if value is not None:
                    self.date = value.date()
                    self.state = 1
                    self.view_date.header = True
                else:
                    self.view_date.error = "Valeur invalide, verifiez que la valeur entrée correspond au format JJ/MM/AAAA, réessayez"
            else:
                if self.oldValue is None:
                    self.date = datetime.now().date()
                else:
                    self.date = self.oldValue.date()
        elif self.state == 1:
            self.view_time.oldValue = self.oldValue.strftime("%H:%M") if self.oldValue is not None else None
            value = self.view_date.render()
            if value != "":
                try:
                    value = datetime.strptime(value, "%H:%M")
                except ValueError:
                    value = None
                if value is not None:
                    self.time = value.time()
                    self.state = 0
                    self.view_time.header = True
                    return MainViewState.BACK, []
                else:
                    self.view_date.error = "Valeur invalide, verifiez que la valeur entrée correspond au format HH:MM, réessayez"
            else:
                if self.oldValue is None:
                    self.time = datetime.now().time()
                else:
                    self.time = self.oldValue.time()
        return None, None


class EditTournamentStyleController(ItemSelectionController[str]):

    @property
    def value(self):
        if self.selected_index == 1:
            return StyleTournament.FAST_STRIKE
        elif self.selected_index == 2:
            return StyleTournament.BLITZ
        return self.oldValue

    def __init__(self, /, *choices: T):
        super().__init__(
            "Bullet",
            "Coup rapide",
            "Blitz",
        )
        self.oldValue: StyleTournament = StyleTournament.BULLET
        self.view.can_repeat_list = False
        self.view.can_save = False

    def run(self):
        self.view.exitName = f"Valeure par defaut: {StyleTournament(self.oldValue).name}"
        return super().run()
