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
            View.clear_screen()
            if self.title != "" and self.title is not None:
                View.render_title(self.title)
            i = 0
            for choice in self.choices:
                if isinstance(choice, str):
                    print("%d)" % i, choice)
                else:
                    choice.render()
                i += 1
            print('----')
            if self.can_save:
                print("s)", "Sauvegarder")
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
