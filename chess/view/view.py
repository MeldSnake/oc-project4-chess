import os


class View:

    @classmethod
    def clear_screen(cls):
        if os.name == "posix":
            os.system('clear')
        else:
            os.system('cls')

    @classmethod
    def render_title(cls, title: str):
        print("+", "-"*len(title), "+", sep='-')
        print("+", title, "+")
        print("+", "-"*len(title), "+", sep='-')

    def render(self):
        raise NotImplementedError()
