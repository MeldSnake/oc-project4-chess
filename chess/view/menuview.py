from chess.view.view import View


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
