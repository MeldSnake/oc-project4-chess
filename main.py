from chess.controllers.maincontroller import MainController

from chess.database.dbadapter import DBAdapter


if __name__ == "__main__":
    with DBAdapter() as db:
        ctrl = MainController(db)
        ctrl.run()
