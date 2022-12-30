from chess.controllers.maincontroller import MainController

from chess.database.dbadapter import DBAdapter


if __name__ == "__main__":
    db = DBAdapter()
    ctrl = MainController(db)
    ctrl.run()
