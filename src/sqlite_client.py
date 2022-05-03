import sqlite3
from dataclasses import dataclass, field
from sqlite3.dbapi2 import Connection, Cursor

from abstracts import AbstractSqlClient
from commons import (
    QUERY_CREATE_USER_TABLE,
    QUERY_CREATE_WORD_TABLE,
    QUERY_INSERT_USER,
    QUERY_INSERT_WORD,
    QUERY_SELECT_USER,
    QUERY_SELECT_WORD,
    QUERY_UPDATE_USER,
    QUERY_UPDATE_WORD,
    TYPE_USER,
    TYPE_WORD,
)


@dataclass
class SqliteClient(AbstractSqlClient):
    db_name: str
    connection: Connection = field(init=False)
    cursor: Cursor = field(init=False)

    def __post_init__(self) -> None:
        # データベースにアクセス / データベースの作成
        self.connection = sqlite3.connect(self.db_name, isolation_level=None)
        self.connection.row_factory = self.__dict_factory
        # カーソルオブジェクトを取得
        self.cursor = self.connection.cursor()
        # テーブル作成 / テーブルが存在しない場合のみ新規作成
        self.cursor.execute(QUERY_CREATE_USER_TABLE)
        self.cursor.execute(QUERY_CREATE_WORD_TABLE)

    # データ取得時にデータを辞書型で返すように修正
    def __dict_factory(self, cursor, row) -> dict:
        results = {}
        for i, column in enumerate(cursor.description):
            results[column[0]] = row[i]
        return results

    # SQL文をSqliteのプレースホルダーを使用するフォーマットの文字列に置換
    def __sqlite_query(self, sql: str) -> str:
        return sql.format("?")

    # ユーザの追加
    def insert_user(self, discord_user_id: int, name: str, voice: str) -> None:
        sql = self.__sqlite_query(QUERY_INSERT_USER)
        self.cursor.execute(sql, (discord_user_id, name, voice))
        return

    # ユーザの取得
    def select_user(self, discord_user_id: int) -> TYPE_USER:
        sql = self.__sqlite_query(QUERY_SELECT_USER)
        self.cursor.execute(sql, (discord_user_id,))
        return self.cursor.fetchone()

    # ユーザの更新
    def update_user(self, discord_user_id: int, name: str, voice: str) -> None:
        sql = self.__sqlite_query(QUERY_UPDATE_USER)
        self.cursor.execute(sql, (name, voice, discord_user_id))
        return

    def insert_word(
        self, discord_server_id: str, word: str, reading: str
    ) -> None:
        sql = self.__sqlite_query(QUERY_INSERT_WORD)
        self.cursor.execute(sql, (discord_server_id, word, reading))
        return

    def select_word(self, discord_server_id: str, word: str) -> TYPE_WORD:
        sql = self.__sqlite_query(QUERY_SELECT_WORD)
        self.cursor.execute(sql, (discord_server_id, word))
        return self.cursor.fetchone()

    def update_word(
        self, discord_server_id: str, word: str, reading: str
    ) -> None:
        sql = self.__sqlite_query(QUERY_UPDATE_WORD)
        self.cursor.execute(sql, (reading, discord_server_id, word))
        return
