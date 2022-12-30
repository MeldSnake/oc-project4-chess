from chess.view.view import View


class MenuItemsView(View):

    def __init__(self) -> None:
        super().__init__()
        self.choices: list[View | str] = []
        self.exitName = "Quitter"
        self.empty_text: str | None = None
        self.show_header = True
        self.can_save = True
        self.title: str | None = None
        self.can_repeat_list = True
        self.err_str: str | None = None
        self.before_view: View | None = None
        self.no_input = False

    def render(self):
        if self.err_str:
            print(self.err_str)
            return None
        if self.show_header:
            View.clear_screen()
            if self.before_view is not None:
                self.before_view.render()
            if self.title != "" and self.title is not None:
                View.render_title(self.title)
            i = 0
            if len(self.choices) == 0:
                if self.empty_text is not None:
                    print(self.empty_text)
            else:
                for choice in self.choices:
                    if isinstance(choice, str):
                        print("%d)" % i, choice)
                    else:
                        choice.render()
                    i += 1
            if not self.no_input:
                print('----')
                if self.can_save:
                    print("s)", "Sauvegarder")
                if self.can_repeat_list:
                    print("?)", "Affiche l'index des choix")
                print("q)", self.exitName)
        if self.no_input:
            return ""
        try:
            user_input = input("Choisissez une option: ")
        except KeyboardInterrupt:
            user_input = ""
        except EOFError:
            user_input = ""
        return user_input
