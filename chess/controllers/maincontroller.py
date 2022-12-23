from typing import Any, Type
from chess.controllers.controller import Controller
from chess.controllers.mainstate import MainViewState
import chess.controllers.menucontrollers as mc
import chess.controllers.menueditcontrollers as mec
import chess.controllers.editcontrollers as ec
from chess.controllers.reportcontrollers import ReportPlayersController, ReportRoundsController, ReportTournamentsController, ReportsMatchsController
from chess.database.dbadapter import DBAdapter
from chess.models.match import Match
from chess.models.player import Player
from chess.models.round import Round
from chess.models.tournament import Tournament
import copy


class MainController(Controller):
    """Main class handling the logic behind the root View."""

    @property
    def current_controller(self):
        """Current controller being or to be displayed"""
        if len(self.previous_controllers) == 0:
            return None
        return self.previous_controllers[-1]

    def __init__(self, db: DBAdapter):
        self._db = db
        self.players: list[Player] = []
        self.tournaments: list[Tournament] = []
        self.rounds: list[Round] = []
        self.matchs: list[Match] = []
        self.states: list[MainViewState] = []
        self.previous_controllers: list[Controller] = []

        self.current_player: Player | None = None
        self.current_tournament: Tournament | None = None
        self.current_round: Round | None = None
        self.current_match: Match | None = None
        self.edited_data: Player | Tournament | Round | Match | None = None
        self.edited_field: str | None = None
        self.edited_type: Type[Any] | None

    def _clearFields(self):
        """Clear all data within the controller, reseting it to default values"""
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
        """Called upon requesting a database load, this also reset the states to the MAIN_MENU"""
        self._clearFields()

        self.players = list(self._db.all(Player))
        self.tournaments = list(self._db.all(Tournament))
        self.rounds = list(self._db.all(Round))
        self.matchs = list(self._db.all(Match))

        self.states.append(MainViewState.MAIN_MENU)

    def onSaveDatabase(self, *_):
        """Called upon requesting a database save"""
        self._db.save(*self.players)
        self._db.save(*self.tournaments)
        self._db.save(*self.rounds)
        self._db.save(*self.matchs)

    def run(self):
        """Main loop that runs all sub controllers and contains the root logic"""
        self.onLoadDatabase()
        self.previous_controllers: list[Controller] = []
        while len(self.states) > 0:
            current_state = self.states[-1]
            new_state = None
            if current_state in MAPPED_STATE_METHODS:
                new_state = MAPPED_STATE_METHODS[current_state](self)
            if new_state is not None:
                if new_state in MENU_RESETS:
                    self.previous_controllers.pop()
                self.states.append(new_state)

    def _save_item(self):
        """SAVE_ITEM: Save the currently edited item on the database depending on the state that requested it"""
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

    def _unsupported(self):
        """Default behaviour when an unknown/non-implemented state """
        assert False, "Etat non supporté"
        self.states.pop()
        return None

    def _quit(self):
        """QUIT: Reset the controller to its default values"""
        self._clearFields()
        return None

    def _save_database(self):
        """SAVE_DATABASE: save all items onto the database"""
        self.onSaveDatabase()
        self.states.pop()
        return None

    def _load_database(self):
        """LOAD_DATABASE: resets the controller and load all data from the database, ignoring pending changes"""
        self.onLoadDatabase()
        self.states.pop()
        return None

    def _back(self):
        """BACK: Return back to the previous state"""
        self.states.pop()
        self.states.pop()
        self.previous_controllers.pop()
        return None

    def _edit_field(self):
        """EDIT_FIELD: render the edit view for the current field being edited on the current item"""
        current_controller = self.current_controller
        if self.edited_field is None or self.edited_data is None:
            self.states.pop()
        else:
            if self.edited_field in ["start_time", "end_time"]:
                if not isinstance(current_controller, ec.EditDatetimeController):
                    current_controller = ec.EditDatetimeController()
                    self.previous_controllers.append(current_controller)
            else:
                if not isinstance(current_controller, ec.EditController):
                    current_controller = ec.EditController[Any](self.edited_type)
                    self.previous_controllers.append(current_controller)
            current_controller.oldValue = getattr(self.edited_data, self.edited_field)
            new_state, _ = current_controller.run()
            # if new_state == MainViewState.BACK:
            #     if current_controller.value is not None:
            #         setattr(self.edited_data, self.edited_field, current_controller.value)
            return new_state
        return None

    def _reports_matchs_menu(self):
        """REPORTS_MATCHS_MENU: Report all matchs from the current round (or all if None currently set)"""
        current_controller = self.current_controller
        if not isinstance(current_controller, ReportsMatchsController):
            if self.current_round is not None:
                current_controller = ReportsMatchsController(*[r for r in self.matchs if r.round is self.current_round])
            else:
                current_controller = ReportsMatchsController(*self.matchs)
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        return new_state

    def _reports_rounds_menu(self):
        """REPORTS_ROUNDS_MENU: Report all rounds and query which one to report matchs about."""
        current_controller = self.current_controller
        if not isinstance(current_controller, ReportRoundsController):
            if self.current_tournament is not None:
                # TODO Obtain all rounds from current_round
                current_controller = ReportRoundsController(*[x for x in self.rounds if x.tournament == self.current_tournament])
            else:
                current_controller = ReportRoundsController(*self.rounds)
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state in [MainViewState.REPORTS_MATCHS_MENU, MainViewState.REPORTS_PLAYERS]:
            self.current_round = current_controller.selected_item  # type: ignore
        else:
            self.current_round = None
        return new_state

    def _reports_tournaments_menu(self):
        """REPORTS_TOURNAMENTS_MENU: Report all tournaments and query which one to report rounds about."""
        current_controller = self.current_controller
        if not isinstance(current_controller, ReportTournamentsController):
            current_controller = ReportTournamentsController(*self.tournaments)
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state in [MainViewState.REPORTS_ROUNDS_MENU, MainViewState.REPORTS_PLAYERS]:
            self.current_tournament = current_controller.selected_item  # type: ignore
        else:
            self.current_tournament = None
        return new_state

    def _reports_players(self):
        """REPORTS_PLAYERS: Report all players"""
        current_controller = self.current_controller
        if not isinstance(current_controller, ReportPlayersController):
            if self.current_tournament is not None:
                # TODO Obtain all players from the tournament
                current_controller = ReportPlayersController()
            else:
                current_controller = ReportPlayersController(*self.players)
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        return new_state

    def _reports_menu(self):
        """REPORTS_MENU: Prompt which report type the user desire to access"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mc.ReportsMenuController):
            current_controller = mc.ReportsMenuController()
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        return new_state

    def _continue_tournament(self):
        """CONTINUE_TOURNAMENT: Continue the current tournament from where it was last left"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mc.ContinueTournamentController):
            current_controller = mc.ContinueTournamentController()
            self.previous_controllers.append(current_controller)
        current_controller.is_tournament_finished = self.current_tournament.finished  # type: ignore
        new_state, _ = current_controller.run()
        return new_state

    def _continue_tournament_menu(self):
        """CONTINUE_TOURNAMENT_MENU: Prompt which tournament the user wants to continue"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mec.ContinueTournamentMenuController):
            current_controller = mec.ContinueTournamentMenuController(
                            *[x for x in self.tournaments if not x.finished]
                        )
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        return new_state

    def _edit_match(self):
        """EDIT_MATCH: Modify the current match"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mec.EditMatchController):
            current_controller = mec.EditMatchController()
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state == MainViewState.EDIT_FIELD:
            self.edited_field = current_controller.field_edit
            self.edited_type = current_controller.vtype
        return new_state

    def _edit_match_menu(self):
        """EDIT_MATCH_MENU: Prompt which match the user wants to edit"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mec.EditMatchMenuController):
            current_controller = mec.EditMatchMenuController(
                *[x for x in self.matchs if x.round == self.current_round]
            )
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state is not None and isinstance(current_controller.selected_item, Match):
            self.current_match = current_controller.selected_item
            self.edited_data = copy.copy(self.current_match)
        return new_state

    def _edit_round(self):
        """EDIT_ROUND: Modify the current round"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mec.EditRoundController):
            current_controller = mec.EditRoundController()
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state == MainViewState.EDIT_FIELD:
            self.edited_field = current_controller.field_edit
            self.edited_type = current_controller.vtype
        return new_state

    def _edit_round_menu(self):
        """EDIT_ROUND_MENU: Prompt which round the user wants to edit"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mec.EditRoundMenuController):
            current_controller = mec.EditRoundMenuController(
                *[x for x in self.rounds if x.tournament == self.current_tournament]
            )
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state is not None and isinstance(current_controller.selected_item, Round):
            self.current_round = current_controller.selected_item
            self.edited_data = copy.copy(self.current_round)
        return new_state

    def _edit_tournament(self):
        """EDIT_TOURNAMENT: Modify the current tournament"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mec.EditTournamentController):
            current_controller = mec.EditTournamentController()
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state == MainViewState.EDIT_FIELD:
            self.edited_field = current_controller.field_edit
            self.edited_type = current_controller.vtype
        return new_state

    def _edit_tournament_menu(self):
        """EDIT_TOURNAMENT_MENU: Prompt which tournament the user wants to edit"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mec.EditTournamentMenuController):
            current_controller = mec.EditTournamentMenuController(*self.tournaments)
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state is not None and isinstance(current_controller.selected_item, Tournament):
            self.current_tournament = current_controller.selected_item
            self.edited_data = copy.copy(self.current_tournament)
        return new_state

    def _new_tournament(self):
        """NEW_TOURNAMENT: Create a new tournament and redirect to EDIT_TOURNAMENT"""
        self.current_tournament = None
        self.edited_data = Tournament()
        self.states.pop()
        return MainViewState.EDIT_TOURNAMENT

    def _tournament_menu(self):
        """TOURNAMENT_MENU: Tournament menu prompting the user to create or edit a tournament"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mc.TournamentsMenuController):
            current_controller = mc.TournamentsMenuController()
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        return new_state

    def _edit_player(self):
        """EDIT_PLAYER: Prompt the user for modifications to the player"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mec.EditPlayerController):
            current_controller = mec.EditPlayerController()
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state == MainViewState.EDIT_FIELD:
            self.edited_field = current_controller.field_edit
            self.edited_type = current_controller.vtype
        return new_state

    def _edit_player_menu(self):
        """EDIT_PLAYER_MENU: Prompt the user which player to edit"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mec.EditPlayerMenuController):
            current_controller = mec.EditPlayerMenuController(*self.players)
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state is not None and isinstance(current_controller.selected_item, Player):
            self.current_player = current_controller.selected_item
            self.edited_data = copy.copy(self.current_player)
        return new_state

    def _new_player(self):
        """NEW_PLAYER: Create a new player and redirect to EDIT_PLAYER"""
        self.current_player = None
        self.edited_data = Player()
        self.states.pop()
        return MainViewState.EDIT_PLAYER

    def _players_menu(self):
        """PLAYERS_MENU: Menu prompting user to create a new user or edit one"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mc.PlayersMenuController):
            current_controller = mc.PlayersMenuController()
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        return new_state

    def _main_menu(self):
        """MAIN_MENU: Promp user with the main menu content"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mc.MainMenuController):
            current_controller = mc.MainMenuController()
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        return new_state


MENU_RESETS = [
    MainViewState.MAIN_MENU,
    MainViewState.PLAYERS_MENU,
    MainViewState.EDIT_PLAYER_MENU,
    MainViewState.TOURNAMENTS_MENU,
    MainViewState.EDIT_TOURNAMENT_MENU,
    MainViewState.EDIT_TOURNAMENT,
    MainViewState.EDIT_ROUND_MENU,
    MainViewState.EDIT_ROUND,
    MainViewState.EDIT_MATCH_MENU,
    MainViewState.EDIT_MATCH,
    MainViewState.CONTINUE_TOURNAMENT_MENU,
    MainViewState.CONTINUE_TOURNAMENT,
    MainViewState.REPORTS_MENU,
    # MainViewState.REPORTS_PLAYERS,
    MainViewState.REPORTS_TOURNAMENTS_MENU,
    MainViewState.REPORTS_ROUNDS_MENU,
    # MainViewState.REPORTS_MATCHS_MENU,
]
"""List of all states that shall redisplay their menu when swithching back to them"""
MAPPED_STATE_METHODS = {
    MainViewState.MAIN_MENU: MainController._main_menu,
    MainViewState.PLAYERS_MENU: MainController._players_menu,
    MainViewState.NEW_PLAYER: MainController._new_player,
    MainViewState.EDIT_PLAYER_MENU: MainController._edit_player_menu,
    MainViewState.EDIT_PLAYER: MainController._edit_player,
    MainViewState.TOURNAMENTS_MENU: MainController._tournament_menu,
    MainViewState.NEW_TOURNAMENT: MainController._new_tournament,
    MainViewState.EDIT_TOURNAMENT_MENU: MainController._edit_tournament_menu,
    MainViewState.EDIT_TOURNAMENT: MainController._edit_tournament,
    MainViewState.EDIT_ROUND_MENU: MainController._edit_round_menu,
    MainViewState.EDIT_ROUND: MainController._edit_round,
    MainViewState.EDIT_MATCH_MENU: MainController._edit_match_menu,
    MainViewState.EDIT_MATCH: MainController._edit_match,
    MainViewState.CONTINUE_TOURNAMENT_MENU: MainController._continue_tournament_menu,
    MainViewState.CONTINUE_TOURNAMENT: MainController._continue_tournament,
    MainViewState.REPORTS_MENU: MainController._reports_menu,
    MainViewState.REPORTS_PLAYERS: MainController._reports_players,
    MainViewState.REPORTS_TOURNAMENTS_MENU: MainController._reports_tournaments_menu,
    MainViewState.REPORTS_ROUNDS_MENU: MainController._reports_rounds_menu,
    MainViewState.REPORTS_MATCHS_MENU: MainController._reports_matchs_menu,
    MainViewState.EDIT_FIELD: MainController._edit_field,
    MainViewState.SAVE_ITEM: MainController._save_item,
    MainViewState.BACK: MainController._back,
    MainViewState.LOAD_DATABASE: MainController._load_database,
    MainViewState.SAVE_DATABASE: MainController._save_database,
    MainViewState.QUIT: MainController._quit,
    # TODO Missing
    # case MainViewState.CHOOSE_MATCH_WINNER:
    # case MainViewState.SET_MATCH_SCORE:
    # case MainViewState.EDIT_TOURNAMENT_STYLE:
}
"""Map all available consollers with their method counterpart"""
