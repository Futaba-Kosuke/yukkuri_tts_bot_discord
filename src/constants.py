from typing import Final, TypedDict

COMMAND_PREFIX: Final[str] = "!"

SUMMON_SUCCESS_MESSAGE: Final[str] = "ゆっくりしていってね！"
SUMMON_FAILURE_MESSAGE: Final[str] = "ボイスチャンネルに入ってから話しかけてね！"
BYE_SUCCESS_MESSAGE: Final[str] = "また呼んでね！"
BYE_FAILURE_MESSAGE: Final[str] = "ボイスチャンネルに入ってないよ！"

WELCOME_MESSAGE: Final[str] = "{}さん、いらっしゃい。ゆっくりしていってね！"
FAREWELL_MESSAGE: Final[str] = "{}さん、さようなら。また来てね！"
CHANGE_SUCCESS_REIMU_MESSAGE: Final[str] = "ゆっくり霊夢よ。{}さんのコメントは私が読み上げさせて貰うわね。"
CHANGE_SUCCESS_MARISA_MESSAGE: Final[str] = "ゆっくり魔理沙だぜ。{}さんのコメントは私が読み上げさせて貰うぜ。"
CHANGE_FAILURE_MESSAGE: Final[str] = "読み上げは `霊夢` か `魔理沙` のどちらかに頼んでね！"

DB_NAME: Final[str] = "database.db"
QUERY_CREATE_USER_TABLE: Final[
    str
] = """
CREATE TABLE IF NOT EXISTS users (
    discord_user_id INTEGER PRIMARY KEY,
    name VARCHAR,
    voice VARCHAR
)
"""
QUERY_INSERT_USER: Final[
    str
] = """
INSERT INTO users(discord_user_id, name, voice) values({0}, {0}, {0})
"""
QUERY_SELECT_USER_FROM_DISCORD_USER_ID: Final[
    str
] = """
SELECT * FROM users WHERE discord_user_id = {0}
"""
QUERY_UPDATE_USER_FROM_DISCORD_USER_ID: Final[
    str
] = """
UPDATE users SET name = {0}, voice = {0} WHERE discord_user_id = {0}
"""
TYPE_USER: Final[TypedDict] = TypedDict(
    "TYPE_USER", {"discord_user_id": int, "name": str, "voice": str}
)
