import pathlib
from typing import Generator, Type, TypeVar
from weakref import WeakSet

from tinydb import TinyDB
from tinydb.table import Document

from chess.models.model import Model
from chess.models.player import Player
from chess.models.tournament import Tournament
from chess.models.round import Round
from chess.models.match import Match
from chess.serializers import deserialize_date, deserialize_datetime, serialize_date, serialize_datetime


TModel = TypeVar('TModel', bound=Model)


class DBAdapter:

    def __init__(self):
        self.__dbPath = pathlib.Path(".") / pathlib.Path("db.json")
        self.__db: TinyDB | None = None
        self.__types_refs: dict[Type[Model], WeakSet[Model]] = {}

    def __enter__(self):
        self.__db = TinyDB(self.__dbPath)
        return self

    def __exit__(self, *_):
        if self.__db is not None:
            self.__db.close()
        self.__db = None

    def register_model(self, value: Model):
        self._ensure_refs(type(value))
        refs = self.__types_refs[type(value)]
        if value not in refs:
            refs.add(value)

    def _ensure_refs(self, vtype: Type[TModel]) -> WeakSet[TModel]:
        if vtype not in self.__types_refs:
            weak_set = WeakSet[TModel]()
            self.__types_refs[vtype] = weak_set  # type: ignore
            return weak_set
        return self.__types_refs[vtype]  # type: ignore

    def _get_table_name(self, type_: Type[TModel]):
        if type_ is Player:
            return "players"
        elif type_ is Tournament:
            return "tournaments"
        elif type_ is Round:
            return "rounds"
        elif type_ is Match:
            return "matchs"
        return None

    def _table(self, vtype: Type[TModel]):
        if self.__db is None:
            return None
        self._ensure_refs(vtype)
        name = self._get_table_name(vtype)
        if name is None:
            return None
        return self.__db.table(name)

    def _from_player_document(self, document: Document | None) -> Player | None:
        if document is None:
            return None
        model_id: int = document.doc_id
        for ref_ in self._ensure_refs(Player):
            if ref_.model_id == model_id:
                return ref_
        player = Player(
            model_id=model_id,
            first_name=document['first_name'],
            last_name=document['last_name'],
            birthdate=deserialize_date(document['birthdate'], None),
            gender=document['gender'],
            rank=document['rank'],
        )
        self.register_model(player)
        return player

    def _to_player_document(self, player: Player):
        return {
            'first_name': player.first_name,
            'last_name': player.last_name,
            'birthdate': serialize_date(player.birthdate, ""),
            'gender': player.gender,
            'rank': player.rank
        }

    def _from_tournament_document(self, document: Document | None) -> Tournament | None:
        if document is None:
            return None
        model_id: int = document.doc_id
        for ref_ in self._ensure_refs(Tournament):
            if ref_.model_id == model_id:
                return ref_
        tournament = Tournament(
            model_id=model_id,
            name=document['name'],
            where=document['where'],
            when=deserialize_date(document['when']),
            style=document['style'],
            round_count=document['round_count'],
        )
        self.register_model(tournament)
        return tournament

    def _to_tournament_document(self, tournament: Tournament):
        return {
            'name': tournament.name,
            'where': tournament.where,
            'when': serialize_date(tournament.when),
            'style': tournament.style,
            'round_count': tournament.round_count,
            'finished': tournament.finished,
        }

    def _from_round_document(self, document: Document | None) -> Round | None:
        if document is None:
            return None
        model_id: int = document.doc_id
        for ref_ in self._ensure_refs(Round):
            if ref_.model_id == model_id:
                return ref_
        round_ = Round(
            model_id=model_id,
            name=document["name"],
            number=document["number"],
            tournament=self.fromID(Tournament, document['tid']),
        )
        self.register_model(round_)
        if round_.tournament is not None:
            round_.tournament.rounds.append(round_)
        return round_

    def _to_round_document(self, round_: Round):
        return {
            'name': round_.name,
            'number': round_.number,
            'tid': round_.tournament.model_id if round_.tournament is not None else -1,
        }

    def _from_match_document(self, document: Document | None) -> Match | None:
        if document is None:
            return None
        model_id: int = document.doc_id
        for ref_ in self._ensure_refs(Match):
            if ref_.model_id == model_id:
                return ref_
        match_ = Match(
            match_id=model_id,
            mapped_round=self.fromID(Round, document['round']),
            start_time=deserialize_datetime(document['start_time'], None),
            end_time=deserialize_datetime(document['end_time'], None),
            scores=tuple(float(x) for x in document['scores'].split('/')),
            player1=self.fromID(Player, document['player1']),
            player2=self.fromID(Player, document['player2']),
        )
        self.register_model(match_)
        if match_.round is not None:
            match_.round.matchs.append(match_)
        return match_

    def _to_match_document(self, match: Match):
        return {
            'start_time': serialize_datetime(match.start_time,),
            'end_time': serialize_datetime(match.end_time),
            'round': -1 if match.round is None else match.round.model_id,
            'player1': -1 if match.player1 is None else match.player1.model_id,
            'player2': -1 if match.player2 is None else match.player2.model_id,
            'scores': "%.1f/%.1f" % match.scores
        }

    def _from_type_document(self, vtype: Type[TModel], document: Document | None) -> TModel | None:
        if document is None:
            return None
        if vtype is Player:
            return self._from_player_document(document)  # type: ignore
        elif vtype is Tournament:
            return self._from_tournament_document(document)  # type: ignore
        elif vtype is Round:
            return self._from_round_document(document)  # type: ignore
        elif vtype is Match:
            return self._from_match_document(document)  # type: ignore
        return None

    def _to_type_document(self, value: TModel) -> dict | None:
        if isinstance(value, Player):
            return self._to_player_document(value)
        elif isinstance(value, Tournament):
            return self._to_tournament_document(value)
        elif isinstance(value, Round):
            return self._to_round_document(value)
        elif isinstance(value, Match):
            return self._to_match_document(value)
        return None

    def fromID(self, vtype: Type[TModel], model_id: int):
        if model_id < 0:
            return None
        table = self._table(vtype)
        if table is None:
            return None
        document = table.get(doc_id=model_id)
        return self._from_type_document(vtype, document)

    def all(self, vtype: Type[TModel]) -> Generator[TModel, None, None]:
        table = self._table(vtype)
        if table is None:
            return
        refs = self._ensure_refs(vtype)
        for document in table.all():
            found: TModel | None = None
            for ref_ in refs:
                if ref_.model_id == document.doc_id:
                    found = ref_
                    break
            if found is None:
                found = self._from_type_document(vtype, document)
            if found is not None:
                yield found

    def save(self, *values: TModel):
        for value in values:
            dict_document = self._to_type_document(value)
            if dict_document is not None:
                type_val = type(value)
                table = self._table(type_val)
                if value.model_id == -1:
                    self._ensure_refs(type_val)
                    self.register_model(value)
                    value.model_id = table.insert(dict_document)  # type: ignore
                else:
                    table.update(dict_document, doc_ids=[value.model_id])  # type: ignore
                value.updated = True
