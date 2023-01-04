import datetime
from chess.models.match import Match
from chess.models.player import Player
from chess.models.round import Round
from chess.models.tournament import Tournament


class SwissSystem:

    def __init__(self, tournament: Tournament) -> None:
        self.tournament: Tournament = tournament
        if len(self.tournament.rounds) > 0 and len(self.tournament.rounds) < self.tournament.round_count:
            self.round = self.tournament.rounds[0]
        else:
            self.round = None

    def _has_already_fought(self, player1: Player, player2: Player):
        for round_ in self.tournament.rounds:
            for match in round_.matchs:
                if match.player1 is player1 or match.player2 is player1:
                    if match.player1 is player2 or match.player2 is player2:
                        return True
        return False

    def _create_matches(self, round_: Round, players: list[Player]):
        while players != []:
            p1 = players.pop()
            if players == []:
                round_.matchs.append(Match(
                    mapped_round=round_,
                    player1=p1,
                    player2=None,
                    scores=(1.0, 0.0),
                ))
            for p2 in players:
                if not self._has_already_fought(p1, p2):
                    round_.matchs.append(Match(
                        mapped_round=round_,
                        player1=p1,
                        player2=p2,
                    ))
                    players.remove(p2)
                    break

    def _create_round(self, players: list[Player] | None = None):
        self.round = Round(
            name=f"Round {len(self.tournament.rounds) + 1}",
            number=len(self.tournament.rounds) + 1,
            tournament=self.tournament,
            start_time=datetime.datetime.now(),
        )
        if players is None:
            players = list(map(lambda x: x[0], sorted(self.tournament.scores.items(), key=lambda x: (x[1], x[0].rank))))
        self._create_matches(self.round, players)
        self.tournament.rounds.append(self.round)

    def first_round(self, players: list[Player]):
        if self.tournament.rounds != []:
            return
        self.round = Round(
            name="Round 1",
            number=1,
            tournament=self.tournament,
            start_time=datetime.datetime.now(),
        )
        higher_half = players[:len(players) // 2]
        lower_half = players[len(players) // 2:]
        while higher_half != [] and lower_half != []:
            self.round.matchs.append(Match(
                mapped_round=self.round,
                player1=higher_half.pop(0),
                player2=lower_half.pop(0),
            ))
        if higher_half != [] or lower_half != []:
            self.round.matchs.append(Match(
                mapped_round=self.round,
                player1=higher_half.pop() if higher_half != [] else lower_half.pop(),
                player2=None,
                scores=(1.0, 0.0),
            ))
        self.tournament.rounds.append(self.round)
        return self.round

    def next_round(self):
        if self.tournament.round_count == len(self.tournament.rounds):
            return None
        self._create_round()
        return self.round
