from chess.view.view import View


class EditView(View):
    def __init__(self) -> None:
        super().__init__()
        self.oldValue: str | None = None
        self.header = True
        self.error: str | None = None
        self.pre_header: str | None = None

    def render(self):
        if self.header:
            print()
            if self.pre_header is not None:
                print(self.pre_header)
            if self.oldValue is not None:
                print("Ancienne valeur: %s" % self.oldValue)
            print("Pour annuler la modification entré une valeure vide")
            self.header = False
        if self.error is not None:
            print(self.error)
            self.error = None
        try:
            valeur = input("Valeur: ")
        except (KeyboardInterrupt, EOFError):
            valeur = ""
        if valeur != "":
            print()
        return valeur
