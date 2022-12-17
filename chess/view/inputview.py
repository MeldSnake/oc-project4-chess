from chess.view.view import View


class InputView(View):
    def __init__(self) -> None:
        super().__init__()
        self.prompt = ""

    def render(self):
        try:
            value = input(self.prompt)
        except EOFError:
            value = ""
        except KeyboardInterrupt:
            value = ""
        return value
