import sys
import datetime
from typing import Any, Type
from chess.algorithm import SwissSystem
from chess.controllers.controller import Controller
from chess.controllers.mainstate import MainViewState
import chess.controllers.menucontrollers as mc
import chess.controllers.menueditcontrollers as mec
import chess.controllers.editcontrollers as ec
import chess.controllers.reportcontrollers as rc
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
        self.current_system: SwissSystem | None = None

        self.edited_data: Player | Tournament | Round | Match | None = None
        self.edited_field: str | None = None
        self.edited_type: Type[Any] | None

        self.selected_item: Player | Tournament | Round | Match | None = None
        self.selected_players: list[Player] = []

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

        with self._db as db:
            self.players = list(db.all(Player))
            self.tournaments = list(db.all(Tournament))
            self.rounds = list(db.all(Round))
            self.matchs = list(db.all(Match))

        self.states.append(MainViewState.MAIN_MENU)

    def onSaveDatabase(self, *_):
        """Called upon requesting a database save"""

        with self._db as db:
            db.save(*self.players)
            db.save(*self.tournaments)
            db.save(*self.rounds)
            db.save(*self.matchs)

    def run(self):
        """Main loop that runs all sub controllers and contains the root logic"""
        self.onLoadDatabase()
        self.previous_controllers: list[Controller] = []
        while len(self.states) > 0:
            current_state = self.states[-1]
            new_state = MAPPED_STATE_METHODS.get(current_state, MainController._unsupported)(self)
            if new_state is not None:
                self.states.append(new_state)

    def _select_tournament(self):
        current_controller = self.current_controller
        if self.current_tournament is None:
            self.selected_item = None
            return MainViewState.BACK
        if not isinstance(current_controller, mec.TournamentSelectionController):
            current_controller = mec.TournamentSelectionController(*self.tournaments)
            self.previous_controllers.append(current_controller)
        state, _ = current_controller.run()
        self.selected_item = current_controller.selected_item
        if state == MainViewState.BACK:
            self.previous_controllers.pop()
        return state

    def _select_round(self):
        current_controller = self.current_controller
        if self.current_tournament is None:
            self.selected_item = None
            return MainViewState.BACK
        if not isinstance(current_controller, mec.RoundSelectionController):
            current_controller = mec.RoundSelectionController(*self.current_tournament.rounds)
            self.previous_controllers.append(current_controller)
        state, _ = current_controller.run()
        self.selected_item = current_controller.selected_item
        if state == MainViewState.BACK:
            self.previous_controllers.pop()
        return state

    def _select_match(self):
        current_controller = self.current_controller
        if self.current_round is None:
            self.selected_item = None
            return MainViewState.BACK
        if not isinstance(current_controller, mec.MatchSelectionController):
            current_controller = mec.MatchSelectionController(*self.current_round.matchs)
            self.previous_controllers.append(current_controller)
        state, _ = current_controller.run()
        self.selected_item = current_controller.selected_item
        if state == MainViewState.BACK:
            self.previous_controllers.pop()
        return state

    def _select_player(self):
        current_controller = self.current_controller
        if not isinstance(current_controller, mec.PlayerSelectionController):
            current_controller = mec.PlayerSelectionController()
            self.previous_controllers.append(current_controller)
        current_controller.update_choices(*filter(lambda x: x not in self.selected_players, self.players))
        state, _ = current_controller.run()
        self.selected_item = current_controller.selected_item
        if self.selected_item is not None:
            self.selected_players.append(self.selected_item)
        if state == MainViewState.BACK:
            self.previous_controllers.pop()
        return state

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
        assert False, "Etat non supporté {}".format(self.states[-1].name)
        self.states.pop()
        return None

    def _quit(self):
        """QUIT: Reset the controller to its default values"""
        self._clearFields()
        return None

    def _save_database(self):
        """SAVE_DATABASE: save all items onto the database"""
        print("Saving to database", file=sys.stderr)
        self.onSaveDatabase()
        self.states.pop()
        return None

    def _load_database(self):
        """LOAD_DATABASE: resets the controller and load all data from the database, ignoring pending changes"""
        print("Reloading from database", file=sys.stderr)
        self.onLoadDatabase()
        self.states.pop()
        return None

    def _back(self):
        """BACK: Return back to the previous state"""
        self.states.pop()
        self.states.pop()
        return None

    def _edit_field(self):
        """EDIT_FIELD: render the edit view for the current field being edited on the current item"""
        current_controller = self.current_controller
        if self.edited_field is None or self.edited_data is None:
            self.states.pop()
        else:
            if self.edited_field in ["start_time", "end_time", "when"]:
                if not isinstance(current_controller, ec.EditDatetimeController):
                    current_controller = ec.EditDatetimeController()
                    self.previous_controllers.append(current_controller)
            elif self.edited_field in ["style"]:
                if not isinstance(current_controller, ec.EditTournamentStyleController):
                    current_controller = ec.EditTournamentStyleController()
                    self.previous_controllers.append(current_controller)
            else:
                if not isinstance(current_controller, ec.EditController):
                    current_controller = ec.EditController[Any](self.edited_type)
                    self.previous_controllers.append(current_controller)
            current_controller.oldValue = getattr(self.edited_data, self.edited_field)
            new_state, _ = current_controller.run()
            if new_state == MainViewState.BACK:
                if current_controller.value is not current_controller.oldValue:
                    setattr(self.edited_data, self.edited_field, current_controller.value)
                self.previous_controllers.pop()
            return new_state
        return None

    def _reports_matchs_menu(self):
        """REPORTS_MATCHS_MENU: Report all matchs from the current round (or all if None currently set)"""
        current_controller = self.current_controller
        if not isinstance(current_controller, rc.ReportsMatchsController):
            if self.current_round is not None:
                current_controller = rc.ReportsMatchsController(*[r for r in self.matchs if r.round is self.current_round])
            else:
                current_controller = rc.ReportsMatchsController(*self.matchs)
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state == MainViewState.BACK:
            self.previous_controllers.pop()
        return new_state

    def _reports_rounds_menu(self):
        """REPORTS_ROUNDS_MENU: Report all rounds and query which one to report matchs about."""
        if self.current_tournament is None:
            return MainViewState.BACK
        current_controller = self.current_controller
        if not isinstance(current_controller, rc.ReportRoundsController):
            current_controller = rc.ReportRoundsController(*self.current_tournament.rounds)
            current_controller.select_state = MainViewState.REPORTS_MATCHS_MENU
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state not in [None, MainViewState.BACK]:
            self.current_round = current_controller.selected_item  # type: ignore
        else:
            self.current_round = None
        if new_state == MainViewState.BACK:
            self.current_round = None
            self.previous_controllers.pop()
        return new_state

    def _reports_tournaments_menu(self):
        """REPORTS_TOURNAMENTS_MENU: Report all tournaments and query which one to report rounds about."""
        current_controller = self.current_controller
        if not isinstance(current_controller, rc.ReportTournamentsController):
            current_controller = rc.ReportTournamentsController(*self.tournaments)
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state not in [None, MainViewState.BACK]:
            self.current_tournament = current_controller.selected_item  # type: ignore
        else:
            self.current_tournament = None
        if new_state == MainViewState.BACK:
            self.current_tournament = None
            self.previous_controllers.pop()
        return new_state

    def _reports_players_alpha(self):
        """REPORTS_PLAYERS: Report all players"""
        current_controller = self.current_controller
        if not isinstance(current_controller, rc.ReportPlayersController):
            if self.current_tournament is not None:
                players = sorted(self.current_tournament.scores.keys(), key=lambda x: (x.first_name, x.last_name, x.rank))
            else:
                players = sorted(self.players, key=lambda x: (x.first_name, x.last_name, x.rank))
            current_controller = rc.ReportPlayersController(*players)
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state == MainViewState.BACK:
            self.previous_controllers.pop()
        return new_state

    def _reports_players_rank(self):
        """REPORTS_PLAYERS: Report all players"""
        current_controller = self.current_controller
        if not isinstance(current_controller, rc.ReportPlayersController):
            if self.current_tournament is not None:
                players = sorted(self.current_tournament.scores.keys(), key=lambda x: (x.rank, x.last_name, x.first_name))
            else:
                players = sorted(self.players, key=lambda x: (x.rank, x.last_name, x.first_name))
            current_controller = rc.ReportPlayersController(*players)
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state == MainViewState.BACK:
            self.previous_controllers.pop()
        return new_state

    def _reports_players_score(self):
        """REPORTS_PLAYERS: Report all players"""
        current_controller = self.current_controller
        if not isinstance(current_controller, rc.ReportPlayersController):
            if self.current_tournament is not None:
                players = map(lambda x: x[0], sorted(self.current_tournament.scores.items(), key=lambda x: (x[1], x[0].rank, x[0].last_name, x[0].first_name)))
            else:
                players = sorted(self.players, key=lambda x: (x.rank, x.last_name, x.first_name))
            current_controller = rc.ReportPlayersController(*players)
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state == MainViewState.BACK:
            self.previous_controllers.pop()
        return new_state

    def _reports_menu(self):
        """REPORTS_MENU: Prompt which report type the user desire to access"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mc.ReportsMenuController):
            current_controller = mc.ReportsMenuController()
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state == MainViewState.BACK:
            self.previous_controllers.pop()
        return new_state

    def _continue_tournament_menu(self):
        """CONTINUE_TOURNAMENT_MENU: Prompt which tournament the user wants to continue"""
        self.current_tournament = None
        self.current_round = None
        self.current_match = None
        self.current_player = None
        self.current_system = None
        current_controller = self.current_controller
        if not isinstance(current_controller, mec.TournamentSelectionController):
            current_controller = mec.TournamentSelectionController(
                *[x for x in self.tournaments if not x.finished]
            )
            self.previous_controllers.append(current_controller)
        else:
            current_controller.update_choices(
                *[x for x in self.tournaments if not x.finished]
            )
        new_state, _ = current_controller.run()
        if isinstance(current_controller.selected_item, Tournament):
            self.current_tournament = current_controller.selected_item
            self.current_system = SwissSystem(self.current_tournament)
            return MainViewState.CONTINUE_TOURNAMENT
        if new_state == MainViewState.BACK:
            self.current_tournament = None
            self.previous_controllers.pop()
        return new_state

    def _continue_tournament(self):
        """CONTINUE_TOURNAMENT: Continue the current tournament from where it was last left"""
        if self.current_tournament is None:
            self.current_round = None
            self.current_match = None
            self.current_player = None
            self.current_system = None
            return MainViewState.BACK
        if self.current_system is None:
            self.current_system = SwissSystem(self.current_tournament)
        if self.current_tournament.finished:
            return MainViewState.CONTINUE_FINISHED_TOURNAMENT
        if len(self.current_tournament.rounds) == 0:
            return MainViewState.CONTINUE_INIT_TOURNAMENT
        elif self.current_tournament.rounds[-1].finished:
            self.current_round = None
            return MainViewState.CONTINUE_FINISHED_ROUND
        else:
            self.current_round = self.current_tournament.rounds[-1]
            return MainViewState.CONTINUE_STARTED_ROUND
        return None

    def _continue_init_tournament(self):
        # Select players
        if self.current_system is None:
            self.current_round = None
            self.current_match = None
            self.current_player = None
            self.current_system = None
            return MainViewState.BACK
        current_controller = self.current_controller
        if not isinstance(current_controller, mc.ContinueInitTournamentController):
            current_controller = mc.ContinueInitTournamentController(self.current_system)  # type: ignore
            self.previous_controllers.append(current_controller)
        state, _ = current_controller.run()
        if state == MainViewState.CONTINUE_STARTED_ROUND:
            self.current_round = self.current_system.first_round(self.selected_players)
            self.rounds.append(self.current_round)  # type: ignore
            self.matchs.extend(self.current_round.matchs)  # type: ignore
            self.selected_players = []
            self.states.pop()
        if state == MainViewState.BACK:
            self.states.pop()
            self.selected_players = []
        if state is not None:
            self.previous_controllers.pop()
        return state

    def _continue_finished_tournament(self):
        """CONTINUE_FINISHED_TOURNAMENT: Tell the user that the tournament has already been finished"""
        if self.current_tournament is None:
            self.current_round = None
            self.current_match = None
            self.current_player = None
            self.current_system = None
            return MainViewState.BACK
        current_controller = self.current_controller
        if not isinstance(current_controller, mc.ContinueFinishedTournamentController):
            current_controller = mc.ContinueFinishedTournamentController(self.current_system)  # type: ignore
            self.previous_controllers.append(current_controller)
        state, _ = current_controller.run()
        if state is not None:
            self.states.pop()
            self.previous_controllers.pop()
        return state

    def _continue_started_round(self):
        """CONTINUE_STARTED_ROUND: Prompt the user to terminate the currently started round"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mc.ContinueStartedRoundController):
            current_controller = mc.ContinueStartedRoundController(self.current_system)  # type: ignore
            self.previous_controllers.append(current_controller)
        state, _ = current_controller.run()
        if state is not None:
            self.states.pop()
            self.previous_controllers.pop()
        return state

    def _continue_end_round(self):
        """CONTINUE_END_ROUND: Terminate the current round"""
        if self.current_round is not None:
            for match in self.current_round.matchs:
                if match.end_time is None:
                    self.current_match = match
                    self.edited_data = match
                    return MainViewState.CONTINUE_END_MATCH
        self.current_round = None
        self.states.pop()
        return MainViewState.BACK

    def _continue_end_match(self):
        """CONTINUE_END_MATCH: Terminate the current match"""
        if self.current_match is not None:
            if self.current_match.end_time is None:
                self.edited_data = self.current_match
                return MainViewState.CHOOSE_MATCH_WINNER
        self.current_match = None
        self.edited_data = None
        self.states.pop()
        return None

    def _choose_winner(self):
        current_controller = self.current_controller
        if isinstance(self.edited_data, Match):
            if not isinstance(current_controller, mc.WinnerChooserController):
                current_controller = mc.WinnerChooserController(
                    self.edited_data.player1,
                    self.edited_data.player2,
                )
                current_controller.select_state = MainViewState.CONTINUE_END_ROUND
                self.previous_controllers.append(current_controller)
            state, _ = current_controller.run()
            if state is None:
                return None
            if state == MainViewState.BACK:
                self.states.pop()
                self.states.pop()
            elif state == MainViewState.CONTINUE_END_ROUND:
                if current_controller.winner is not None:
                    if current_controller.winner is self.edited_data.player1:
                        self.edited_data.scores = (1.0, 0.0)
                    else:
                        self.edited_data.scores = (0.0, 1.0)
                    self.edited_data.updated = True
                    if self.edited_data.end_time is None:
                        self.edited_data.end_time = datetime.datetime.now()
                elif current_controller.equality:
                    self.edited_data.scores = (0.5, 0.5)
                    self.edited_data.updated = True
                    self.edited_data.end_time = datetime.datetime.now()
            self.previous_controllers.pop()
            return MainViewState.BACK
        self.states.pop()
        return None

    def _continue_start_round(self):
        """CONTINUE_START_ROUND: Start the current round"""
        if self.current_round is not None:
            for match in self.current_round.matchs:
                if match.start_time is None:
                    self.current_match = match
                    self.states.pop()
                    return MainViewState.CONTINUE_START_MATCH
        else:
            self.current_round = self.current_system.next_round()  # type: ignore
            self.rounds.append(self.current_round)  # type: ignore
            self.matchs.extend(self.current_round.matchs)  # type: ignore
            self.edited_data = self.current_round
            return MainViewState.EDIT_ROUND
        self.current_round = None
        self.states.pop()
        return MainViewState.BACK

    def _continue_start_match(self):
        """CONTINUE_START_MATCH: Start the current match"""
        if self.current_match is not None:
            if self.current_match.start_time is None:
                self.current_match.start_time = datetime.datetime.now()
        self.current_match = None
        self.states.pop()
        return MainViewState.BACK

    def _continue_finished_round(self):
        """CONTINUE_FINISHED_ROUND: Prompt the user start the next round"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mc.ContinueFinishedRoundController):
            current_controller = mc.ContinueFinishedRoundController(self.current_system)  # type: ignore
            self.previous_controllers.append(current_controller)
        state, _ = current_controller.run()
        if state is not None:
            self.states.pop()
            self.previous_controllers.pop()
        return state

    def _continue_end_tournament(self):
        """CONTINUE_END_TOURNAMENT: Terminate the current tournament"""
        if self.current_tournament is not None:
            self.states.pop()
            return MainViewState.CONTINUE_FINISHED_TOURNAMENT
        self.states.pop()
        return MainViewState.BACK

    def _edit_match(self):
        """EDIT_MATCH: Modify the current match"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mec.EditMatchController):
            current_controller = mec.EditMatchController()
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        self.edited_data = self.current_match
        if new_state == MainViewState.EDIT_FIELD:
            self.edited_field = current_controller.field_edit
            self.edited_type = current_controller.vtype
        if new_state == MainViewState.BACK:
            self.current_match = None
            self.previous_controllers.pop()
        return new_state

    def _edit_match_menu(self):
        """EDIT_MATCH_MENU: Prompt which match the user wants to edit"""
        if self.current_round is None:
            return MainViewState.BACK
        current_controller = self.current_controller
        if not isinstance(current_controller, mec.EditMatchMenuController):
            current_controller = mec.EditMatchMenuController(
                *self.current_round.matchs
            )
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state is not None and isinstance(current_controller.selected_item, Match):
            self.current_match = current_controller.selected_item
            self.edited_data = copy.copy(self.current_match)
        if new_state == MainViewState.BACK:
            self.current_match = None
            self.previous_controllers.pop()
        return new_state

    def _edit_round(self):
        """EDIT_ROUND: Modify the current round"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mec.EditRoundController):
            current_controller = mec.EditRoundController()
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        self.edited_data = self.current_round
        if new_state == MainViewState.EDIT_FIELD:
            self.edited_field = current_controller.field_edit
            self.edited_type = current_controller.vtype
        if new_state == MainViewState.BACK:
            self.edited_data = self.current_tournament
            self.previous_controllers.pop()
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
        if new_state == MainViewState.BACK:
            self.current_round = None
            self.previous_controllers.pop()
        return new_state

    def _edit_tournament(self):
        """EDIT_TOURNAMENT: Modify the current tournament"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mec.EditTournamentController):
            current_controller = mec.EditTournamentController()
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        self.edited_data = self.current_tournament
        if new_state == MainViewState.EDIT_FIELD:
            self.edited_field = current_controller.field_edit
            self.edited_type = current_controller.vtype
        if new_state == MainViewState.BACK:
            self.edited_data = None
            self.current_tournament = None
            self.previous_controllers.pop()
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
        if new_state == MainViewState.BACK:
            self.current_tournament = None
            self.previous_controllers.pop()
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
        if new_state == MainViewState.BACK:
            self.previous_controllers.pop()
        return new_state

    def _edit_player(self):
        """EDIT_PLAYER: Prompt the user for modifications to the player"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mec.EditPlayerController):
            current_controller = mec.EditPlayerController()
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state == MainViewState.EDIT_FIELD:
            self.edited_data = self.current_player
            self.edited_field = current_controller.field_edit
            self.edited_type = current_controller.vtype
        elif new_state == MainViewState.BACK:
            self.edited_data = None
        if new_state is not None:
            self.previous_controllers.pop()
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
        if new_state == MainViewState.BACK:
            self.previous_controllers.pop()
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
        if new_state == MainViewState.BACK:
            self.previous_controllers.pop()
        return new_state

    def _main_menu(self):
        """MAIN_MENU: Promp user with the main menu content"""
        current_controller = self.current_controller
        if not isinstance(current_controller, mc.MainMenuController):
            current_controller = mc.MainMenuController()
            self.previous_controllers.append(current_controller)
        new_state, _ = current_controller.run()
        if new_state == MainViewState.BACK:
            self.previous_controllers.pop()
        return new_state


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

    MainViewState.CONTINUE_INIT_TOURNAMENT: MainController._continue_init_tournament,
    MainViewState.CONTINUE_FINISHED_TOURNAMENT: MainController._continue_finished_tournament,
    MainViewState.CONTINUE_STARTED_ROUND: MainController._continue_started_round,
    MainViewState.CONTINUE_END_ROUND: MainController._continue_end_round,
    MainViewState.CONTINUE_END_MATCH: MainController._continue_end_match,
    MainViewState.CONTINUE_START_ROUND: MainController._continue_start_round,
    MainViewState.CONTINUE_START_MATCH: MainController._continue_start_match,
    MainViewState.CONTINUE_FINISHED_ROUND: MainController._continue_finished_round,
    MainViewState.CONTINUE_END_TOURNAMENT: MainController._continue_end_tournament,

    MainViewState.REPORTS_MENU: MainController._reports_menu,
    MainViewState.REPORTS_ALPHA_PLAYERS: MainController._reports_players_alpha,
    MainViewState.REPORTS_RANK_PLAYERS: MainController._reports_players_rank,
    MainViewState.REPORTS_SCORE_PLAYERS: MainController._reports_players_score,
    MainViewState.REPORTS_TOURNAMENTS_MENU: MainController._reports_tournaments_menu,
    MainViewState.REPORTS_ROUNDS_MENU: MainController._reports_rounds_menu,
    MainViewState.REPORTS_MATCHS_MENU: MainController._reports_matchs_menu,

    MainViewState.SELECT_TOURNAMENT: MainController._select_tournament,
    MainViewState.SELECT_ROUND: MainController._select_round,
    MainViewState.SELECT_MATCH: MainController._select_match,
    MainViewState.SELECT_PLAYER: MainController._select_player,

    MainViewState.EDIT_FIELD: MainController._edit_field,

    MainViewState.SAVE_ITEM: MainController._save_item,
    MainViewState.LOAD_DATABASE: MainController._load_database,
    MainViewState.SAVE_DATABASE: MainController._save_database,

    MainViewState.BACK: MainController._back,
    MainViewState.QUIT: MainController._quit,

    MainViewState.CHOOSE_MATCH_WINNER: MainController._choose_winner,
    # TODO Missing
    # case MainViewState.EDIT_TOURNAMENT_STYLE:
}
"""Map all available consollers with their method counterpart"""
