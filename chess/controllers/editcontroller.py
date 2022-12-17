from chess.controllers.controller import Controller, MainStateReturn
from typing import Type, TypeVar, Generic
from datetime import date, time, datetime
from chess.controllers.mainstate import MainViewState

from chess.view.view import View

T = TypeVar('T', str, int, float, date, time)


class EditView(View):
    def __init__(self) -> None:
        super().__init__()
        self.oldValue: str | None = None
        self.header = True
        self.error: str | None = None
        self.pre_header: str | None = None

    def render(self):
        if self.header:
            if self.pre_header is not None:
                print(self.pre_header)
            if self.oldValue is not None:
                print("Ancienne valeur: %s" % self.oldValue)
                print("Ecrivez 'annuler' pour revenir en arriere")
            self.header = False
        if self.error is not None:
            print(self.error)
            self.error = None
        try:
            valeur = input("Valeur: ")
        except (KeyboardInterrupt, EOFError):
            valeur = ""
        return valeur


class EditController(Generic[T], Controller):
    def __init__(self, vtype: Type[T]) -> None:
        super().__init__()
        self.vtype = vtype
        self.value: T | None = None
        self.oldValue: T | None = None
        self.view = EditView()

    def deserialize_value(self, value: str) -> T | None:
        if value == "annuler":
            return None
        if self.vtype == str:
            return value  # type: ignore
        if self.vtype == int:
            return int(value)  # type: ignore
        if self.vtype == float:
            return float(value)  # type: ignore
        if self.vtype == date:
            try:
                dt = datetime.strptime(value, "%d/%m/%Y")  # type: ignore
            except ValueError:
                dt = None
            if dt is None:
                return None
            return dt.date()  # type: ignore
        if self.vtype == time:
            try:
                dt = datetime.strptime(value, "%H:%M")  # type: ignore
            except ValueError:
                dt = None
            if dt is None:
                return None
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
            self.value = self.oldValue
        else:
            self.value = self.deserialize_value(value)
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
        self.view_date.pre_header = "Definition de la partie heure"

    def run(self) -> MainStateReturn:
        if self.state == 0:
            self.view_date.oldValue = self.oldValue.strftime("%d/%m/%Y") if self.oldValue is not None else None
            value = self.view_date.render()
            if value == "annuler":
                self.date = None
                self.time = None
                return MainViewState.BACK, []
            else:
                try:
                    value = datetime.strptime(value, "%d/%m/%Y")
                except ValueError:
                    value = None
                if value is not None:
                    self.date = value.date()
                    self.state = 1
                    self.view_date.header = True
                else:
                    self.view_date.error = "Valeur invalide, verifié que la valeur entrée correspond au format JJ/MM/AAAA, réessayé"
        elif self.state == 1:
            self.view_time.oldValue = self.oldValue.strftime("%H:%M") if self.oldValue is not None else None
            value = self.view_date.render()
            if value == "annuler":
                self.state = 0
                self.view_time.header = True
            else:
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
                    self.view_date.error = "Valeur invalide, verifié que la valeur entrée correspond au format HH:MM, réessayé"
        return None, None
