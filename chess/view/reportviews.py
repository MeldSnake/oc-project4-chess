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
                 round_count=4,
                 round_completed=0,
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
        self.round_completed = round_completed
        self.round_count = round_count

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
            print(", [En cours %d/%d]" % (self.round_completed, self.round_count), end='')
        print()


class RoundReportView(View):
    def __init__(self, /,
                 index: int | None = None,
                 name="",
                 number=-1,
                 start_time: datetime.datetime | None = None,
                 end_time: datetime.datetime | None = None) -> None:
        super().__init__()
        self.index = index
        self.name = name
        self.number = number
        self.start_time = start_time
        self.end_time = end_time

    def render(self):
        if self.index is not None:
            print("%d) " % self.index, end='')
        print("Ronde %d: `%s`" % (self.number, self.name), end='')
        if self.start_time is not None:
            print(",", self.start_time.strftime("%d/%m/%Y %H:%M"), end='')
            if self.end_time is not None:
                print(" ->", self.end_time.strftime("%d/%m/%Y %H:%M"), end='')
            else:
                print(" -> ...", end='')
        else:
            print(", Non commencé", end='')
        print()


class MatchReportView(View):
    def __init__(self, /,
                 index: int | None = None,
                 scores: tuple[float, float] = (0.0, 0.0)) -> None:
        super().__init__()
        self.index = index
        self.scores = scores

    def render(self):
        if self.index is not None:
            print("%d) " % self.index, end='')
            print("Match %d:" % (self.index), end=' ')
        else:
            print("Match:", end=' ')
        print("(%.1f, %.1f), " % self.scores, end='')
        if self.scores == (0.0, 0.0):
            print("[En cours]", end='')
        else:
            print("[Terminé]", end='')
        print()


class TournamentLongReportView(View):
    def __init__(self, /,
                 index=-1,
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
        if self.index != -1:
            print("%s)" % self.index, end='')
        print("Tournoi:", self.name, end='')
        if self.finished:
            print("[Terminé]")
        else:
            print("[En cours]")
        print("\tLieu:", self.where)
        if self.when is not None:
            print("\tDate:", self.when.strftime("%d/%m/%Y"))
        print("\tStyle:", end=' ')
        if self.style == StyleTournament.BULLET:
            print("Bullet")
        elif self.style == StyleTournament.BLITZ:
            print("Blitz")
        else:
            print("Coups rapide")
        print("\tLieu:", self.where)


class RoundLongReportView(View):
    def __init__(self, /,
                 index=-1,
                 name="",
                 number=-1,
                 start_time: datetime.datetime | None = None,
                 end_time: datetime.datetime | None = None) -> None:
        super().__init__()
        self.index = index
        self.name = name
        self.number = number
        self.start_time = start_time
        self.end_time = end_time

    def render(self):
        if self.index != -1:
            print("%d)" % self.index, end=' ')
        print("Ronde:", self.name)
        print("\tNumero:", self.number)
        if self.start_time is not None:
            print("\tDebut:", self.start_time.strftime("%d/%m/%Y %H:%M"))
        if self.end_time is not None:
            print("\tFin:", self.end_time.strftime("%d/%m/%Y %H:%M"))


class MatchLongReportView(View):
    def __init__(self, /,
                 player1: str,
                 player2: str,
                 scores: tuple[float, float] = (0.0, 0.0),
                 ) -> None:
        super().__init__()
        self.scores = scores
        self.player1 = player1
        self.player2 = player2

    def render(self):
        print("Match:")
        print("\tScores", *self.scores)
        print("\tJoueur 1:", self.player1)
        print("\tJoueur 2:", self.player2)
        if self.scores != (0.0, 0.0):
            print("\tVainqueur:", end='')
            if self.scores[0] > self.scores[1]:
                print(self.player1)
            elif self.scores[0] < self.scores[1]:
                print(self.player2)
            else:
                print("Egalité")
            print("Status: Terminé")
        else:
            print("Status: En cours")
