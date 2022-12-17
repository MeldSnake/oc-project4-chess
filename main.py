from tinydb import TinyDB
from chess.controllers.maincontroller import MainController
import pathlib


if __name__ == "__main__":
    with TinyDB(pathlib.Path("./db.json")) as db:
        ctrl = MainController(db)
        ctrl.run()
