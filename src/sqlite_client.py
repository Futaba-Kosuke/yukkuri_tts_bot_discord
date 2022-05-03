import sqlite3
from dataclasses import dataclass, field
from sqlite3.dbapi2 import Connection, Cursor

from abstracts import AbstractSqlClient
from commons import (
    QUERY_CREATE_USER_TABLE,
    QUERY_INSERT_USER,
    QUERY_SELECT_USER_FROM_DISCORD_USER_ID,
    QUERY_UPDATE_USER_FROM_DISCORD_USER_ID,
    TYPE_USER,
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

    def __dict_factory(self, cursor, row):
        results = {}
        for i, column in enumerate(cursor.description):
            results[column[0]] = row[i]
        return results

    def __sqlite_query(self, sql: str) -> str:
        return sql.format("?")

    def insert_user(self, discord_user_id: int, name: str, voice: str) -> None:
        sql = self.__sqlite_query(QUERY_INSERT_USER)
        self.cursor.execute(sql, (discord_user_id, name, voice))
        return

    def select_user_from_discord_user_id(
        self, discord_user_id: int
    ) -> TYPE_USER:
        sql = self.__sqlite_query(QUERY_SELECT_USER_FROM_DISCORD_USER_ID)
        self.cursor.execute(sql, (discord_user_id,))
        return self.cursor.fetchone()

    def update_user_from_discord_user_id(
        self, discord_user_id: int, name: str, voice: str
    ) -> None:
        sql = self.__sqlite_query(QUERY_UPDATE_USER_FROM_DISCORD_USER_ID)
        self.cursor.execute(sql, (name, voice, discord_user_id))
        return
