import datetime
from chess.models.tournament import StyleTournament
from chess.view.view import View


class PlayerReportView(View):
    @property
    def age(self):
        today = datetime.date.today()
        return max(0, today.year - self.birthdate.year)

    def __init__(self, /,
                 index: int | None = None,
                 last_name="",
                 first_name="",
                 birthdate: datetime.date | None = None,
                 gender="",
                 rank=-1) -> None:
        super().__init__()
        self.index = index
        self.last_name = last_name
        self.first_name = first_name
        self.birthdate = birthdate or datetime.date.today()
        self.gender = gender
        self.rank = rank

    def render(self):
        if self.index is not None:
            print("%d) " % self.index, end='')
        print("Classement(%d)" % self.rank, self.first_name, self.last_name, "%d ans" % self.age, self.gender)


class TournamentReportView(View):
    def __init__(self, /,
                 index: int | None = None,
                 name="",
                 where="",
                 when: datetime.date | None = None,
                 style=StyleTournament.BULLET,
                 finished=False) -> None:
        super().__init__()
        self.index = index
        self.name = name
        self.where = where
        self.when = when
        self.style = style
        self.finished = finished

    def render(self):
        if self.index is not None:
            print("%d) " % self.index, end='')
        print("Tournoi: `%s`" % self.name, end='')
        if self.where != "":
            print(" à `%s`" % self.where, end='')
        if self.when is not None:
            print(" le `%s`" % self.when.strftime("%d/%m/%Y"), end='')
        print(", style: ", end='')
        if self.style == StyleTournament.BULLET:
            print("Bullet", end='')
        elif self.style == StyleTournament.BLITZ:
            print("Blitz", end='')
        elif self.style == StyleTournament.FAST_STRIKE:
            print("Coup rapide", end='')
        if self.finished:
            print(", [Terminé]", end='')
        else:
            print(", [En cours]", end='')
        print()


class RoundReportView(View):
    def __init__(self, /,
                 index: int | None = None,
                 name="",
                 number=-1) -> None:
        super().__init__()
        self.index = index
        self.name = name
        self.number = number

    def render(self):
        if self.index is not None:
            print("%d) " % self.index, end='')
        print("Ronde %d: `%s`" % (self.number, self.name))


class MatchReportView(View):
    def __init__(self, /,
                 index: int | None = None,
                 start_time: datetime.datetime | None = None,
                 end_time: datetime.datetime | None = None,
                 scores: tuple[float, float] = (0.0, 0.0)) -> None:
        super().__init__()
        self.index = index
        self.start_time = start_time
        self.end_time = end_time
        self.scores = scores

    def render(self):
        if self.index is not None:
            print("%d) " % self.index, end='')
        print("Match %d:" % (self.index), end=' ')
        if self.start_time is not None:
            print(self.start_time.strftime("%d/%m/%Y %H:%M"), end='')
        if self.end_time is not None:
            print("-", self.end_time.strftime("%d/%m/%Y %H:%M"), end='')
        if self.scores[0] == self.scores[1] and self.scores[0] == 0.0:
            print("(%f, %f), [En cours]" % self.scores, end='')
        else:
            print("(%f, %f), [Terminé]" % self.scores, end='')
        print()


class MenuItemsView(View):

    def __init__(self) -> None:
        super().__init__()
        self.choices: list[View | str] = []
        self.exitName = "Quitter"
        self.show_header = True
        self.can_save = True
        self.title: str | None = None
        self.can_repeat_list = True
        self.err_str: str | None = None

    def render(self):
        if self.err_str:
            print(self.err_str)
            return None
        if self.show_header:
            if self.title != "" and self.title is not None:
                print("+-" + "-" * len(self.title) + "-+")
                print("+", self.title, "+")
                print("+-" + "-" * len(self.title) + "-+")
            i = 0
            for choice in self.choices:
                if isinstance(choice, str):
                    print("%d)" % i, choice)
                else:
                    choice.render()
                i += 1
            if self.can_save:
                print("s)", "Sauvegarder la base de donnée")
            if self.can_repeat_list:
                print("?)", "Affiche l'index des choix")
            print("q)", self.exitName)
        try:
            user_input = input("Choisissez une option: ")
        except KeyboardInterrupt:
            user_input = ""
        except EOFError:
            user_input = ""
        return user_input
