from chess.view.view import View


class TextView(View):
    def __init__(self) -> None:
        super().__init__()
        self.text = ""

    def render(self):
        print(self.text)
