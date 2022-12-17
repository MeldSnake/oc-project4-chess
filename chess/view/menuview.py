import datetime
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
