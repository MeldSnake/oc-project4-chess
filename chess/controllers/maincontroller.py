from typing import Any, Type
from tinydb import TinyDB
from chess.controllers.controller import Controller
from chess.controllers.mainstate import MainViewState
import chess.controllers.menucontrollers as mc
import chess.controllers.editcontroller as ec
from chess.models.match import Match
from chess.models.player import Player
from chess.models.round import Round
from chess.models.tournament import Tournament


class MainController(Controller):

    def __init__(self, db: TinyDB):
        self._db = db
        self.players: list[Player] = []
        self.tournaments: list[Tournament] = []
        self.rounds: list[Round] = []
        self.matchs: list[Match] = []
        self.states: list[MainViewState] = []

        self.current_player: Player | None = None
        self.current_tournament: Tournament | None = None
        self.current_round: Round | None = None
        self.current_match: Match | None = None
        self.edited_data: Player | Tournament | Round | Match | None = None
        self.edited_field: str | None = None
        self.edited_type = type(None)

    def _clearFields(self):
        self.tournaments.clear()
        self.players.clear()
        self.rounds.clear()
        self.matchs.clear()
        self.states.clear()

        self.current_player = None
        self.current_tournament = None
        self.current_round = None
        self.current_match = None
        self.edited_data = None
        self.edited_field = None

    def onLoadDatabase(self):
        self._clearFields()

        self.players = Player.all(self._db)
        self.tournaments = Tournament.all(self._db)
        self.rounds = Round.all(self._db)
        self.matchs = Match.all(self._db)

        self.states.append(MainViewState.MAIN_MENU)

    def onSaveDatabase(self, *_):
        Player.save(self._db, *self.players)
        Tournament.save(self._db, *self.tournaments)
        Match.save(self._db, *self.matchs)
        Round.save(self._db, *self.rounds)

    def run(self):
        self.onLoadDatabase()
        current_controller = None
        while len(self.states) > 0:
            current_state = self.states[-1]
            new_state = None
            match current_state:
                case MainViewState.MAIN_MENU:
                    if not isinstance(current_controller, mc.MainMenuController):
                        current_controller = mc.MainMenuController()
                    new_state, _ = current_controller.run()
                case MainViewState.PLAYERS_MENU:
                    if not isinstance(current_controller, mc.PlayersMenuController):
                        current_controller = mc.PlayersMenuController()
                    new_state, _ = current_controller.run()
                case MainViewState.NEW_PLAYER:
                    self.current_player = None
                    self.edited_data = Player()
                    self.states.pop()
                    new_state = MainViewState.EDIT_PLAYER
                case MainViewState.EDIT_PLAYER_MENU:
                    if not isinstance(current_controller, mc.EditPlayerMenuController):
                        current_controller = mc.EditPlayerMenuController(*self.players)
                    new_state, _ = current_controller.run()
                    if new_state is not None and current_controller.selected_player is not None:
                        self.current_player = current_controller.selected_player
                        self.edited_data = self.current_player.copy()
                case MainViewState.EDIT_PLAYER:
                    if not isinstance(current_controller, mc.EditPlayerController):
                        current_controller = mc.EditPlayerController()
                    new_state, _ = current_controller.run()
                    if new_state == MainViewState.EDIT_FIELD:
                        self.edited_field = current_controller.field_edit
                        self.edited_type = current_controller.vtype
                case MainViewState.TOURNAMENTS_MENU:
                    if not isinstance(current_controller, mc.TournamentsMenuController):
                        current_controller = mc.TournamentsMenuController()
                    new_state, _ = current_controller.run()
                case MainViewState.NEW_TOURNAMENT:
                    self.current_tournament = None
                    self.edited_data = Tournament()
                    self.states.pop()
                    new_state = MainViewState.EDIT_TOURNAMENT
                case MainViewState.EDIT_TOURNAMENT_MENU:
                    if not isinstance(current_controller, mc.EditTournamentMenuController):
                        current_controller = mc.EditTournamentMenuController(*self.tournaments)
                    new_state, _ = current_controller.run()
                    if new_state is not None and current_controller.selected_tournament is not None:
                        self.current_tournament = current_controller.selected_tournament
                        self.edited_data = self.current_tournament.copy()
                case MainViewState.EDIT_TOURNAMENT:
                    if not isinstance(current_controller, mc.EditTournamentController):
                        current_controller = mc.EditTournamentController()
                    new_state, _ = current_controller.run()
                    if new_state == MainViewState.EDIT_FIELD:
                        self.edited_field = current_controller.field_edit
                        self.edited_type = current_controller.vtype
                case MainViewState.EDIT_ROUND_MENU:
                    self.states.pop()
                    pass
                case MainViewState.EDIT_ROUND:
                    self.states.pop()
                    pass
                case MainViewState.EDIT_MATCH_MENU:
                    self.states.pop()
                    pass
                case MainViewState.EDIT_MATCH:
                    self.states.pop()
                    pass
                case MainViewState.CONTINUE_TOURNAMENT_MENU:
                    if not isinstance(current_controller, mc.ContinueTournamentMenuController):
                        current_controller = mc.ContinueTournamentMenuController(
                            *[x for x in self.tournaments if not x.finished]
                        )
                    new_state, _ = current_controller.run()
                case MainViewState.CONTINUE_TOURNAMENT:
                    if not isinstance(current_controller, mc.ContinueTournamentController):
                        current_controller = mc.ContinueTournamentController()
                    new_state, _ = current_controller.run()
                case MainViewState.REPORTS_MENU:
                    self.states.pop()
                    pass
                case MainViewState.REPORTS_PLAYERS:
                    self.states.pop()
                    pass
                case MainViewState.REPORTS_TOURNAMENTS_MENU:
                    self.states.pop()
                    pass
                case MainViewState.REPORTS_ROUNDS_MENU:
                    self.states.pop()
                    pass
                case MainViewState.REPORTS_MATCHS_MENU:
                    self.states.pop()
                    pass
                case MainViewState.EDIT_FIELD:
                    if self.edited_field is None or self.edited_data is None:
                        self.states.pop()
                    else:
                        if self.edited_field in ["start_time", "end_time"]:
                            if not isinstance(current_controller, ec.EditDatetimeController):
                                current_controller = ec.EditDatetimeController()
                        else:
                            if not isinstance(current_controller, ec.EditController):
                                current_controller = ec.EditController(self.edited_type)
                        current_controller.oldValue = getattr(self.edited_data, self.edited_field)
                        new_state, _ = current_controller.run()
                        if new_state == MainViewState.BACK:
                            if current_controller.value is not None:
                                setattr(self.edited_data, self.edited_field, current_controller.value)
                case MainViewState.SAVE_ITEM:
                    self.states.pop()
                    old_state = self.states.pop()
                    if old_state == MainViewState.EDIT_PLAYER:
                        if self.current_player is None:
                            self.players.append(self.edited_data)  # type: ignore
                        else:
                            self.current_player.update(self.edited_data)  # type: ignore
                    elif old_state == MainViewState.EDIT_TOURNAMENT:
                        if self.current_tournament is None:
                            self.tournaments.append(self.edited_data)  # type: ignore
                        else:
                            self.current_tournament.update(self.edited_data)  # type: ignore
                    elif old_state == MainViewState.EDIT_ROUND:
                        if self.current_round is None:
                            self.rounds.append(self.edited_data)  # type: ignore
                        else:
                            self.current_round.update(self.edited_data)  # type: ignore
                    elif old_state == MainViewState.EDIT_MATCH:
                        if self.current_match is None:
                            self.matchs.append(self.edited_data)  # type: ignore
                        else:
                            self.current_match.update(self.edited_data)  # type: ignore
                case MainViewState.BACK:
                    self.states.pop()
                    self.states.pop()
                    current_controller = None
                case MainViewState.LOAD_DATABASE:
                    self.onLoadDatabase()
                    self.states.pop()
                case MainViewState.SAVE_DATABASE:
                    self.onSaveDatabase()
                    self.states.pop()
                case MainViewState.QUIT:
                    self._clearFields()
            if new_state is not None:
                self.states.append(new_state)
