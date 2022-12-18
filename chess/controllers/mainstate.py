from enum import Enum


class MainViewState(int, Enum):
    MAIN_MENU = 0

    PLAYERS_MENU = 1
    NEW_PLAYER = 2
    EDIT_PLAYER_MENU = 3
    EDIT_PLAYER = 4

    TOURNAMENTS_MENU = 5

    NEW_TOURNAMENT = 6
    EDIT_TOURNAMENT_MENU = 7
    EDIT_TOURNAMENT = 8
    EDIT_ROUND_MENU = 9
    EDIT_ROUND = 10
    EDIT_MATCH_MENU = 11
    EDIT_MATCH = 12

    CONTINUE_TOURNAMENT_MENU = 13
    CONTINUE_TOURNAMENT = 14

    REPORTS_MENU = 15
    REPORTS_PLAYERS = 16
    REPORTS_TOURNAMENTS_MENU = 17
    REPORTS_ROUNDS_MENU = 18
    REPORTS_MATCHS_MENU = 19

    CHOOSE_MATCH_WINNER = -9
    SET_MATCH_SCORE = -8
    EDIT_TOURNAMENT_STYLE = -7

    SAVE_ITEM = -6
    EDIT_FIELD = -5
    BACK = -4
    LOAD_DATABASE = -3
    SAVE_DATABASE = -2
    QUIT = -1
