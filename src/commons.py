from typing import Final, TypedDict

COMMAND_PREFIX: Final[str] = "!"

DB_NAME: Final[str] = "database.db"
QUERY_CREATE_USER_TABLE: Final[
    str
] = """
CREATE TABLE IF NOT EXISTS users (
    discord_user_id INTEGER PRIMARY KEY,
    name VARCHAR,
    voice VARCHAR
);
"""
QUERY_INSERT_USER: Final[
    str
] = """
INSERT INTO users(discord_user_id, name, voice) values({0}, {0}, {0});
"""
QUERY_SELECT_USER: Final[
    str
] = """
SELECT * FROM users WHERE discord_user_id = {0};
"""
QUERY_UPDATE_USER: Final[
    str
] = """
UPDATE users SET name = {0}, voice = {0} WHERE discord_user_id = {0};
"""
QUERY_CREATE_WORD_TABLE: Final[
    str
] = """
CREATE TABLE IF NOT EXISTS words (
    word_id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_server_id VARCHAR,
    word VARCHAR,
    reading VARCHAR
);
"""
QUERY_INSERT_WORD: Final[
    str
] = """
INSERT INTO words(discord_server_id, word, reading) values({0}, {0}, {0});
"""
QUERY_SELECT_WORD: Final[
    str
] = """
SELECT * FROM words WHERE discord_server_id = {0}, word = {0};
"""
QUERY_UPDATE_WORD: Final[
    str
] = """
UPDATE words SET reading = {0} WHERE discord_server_id = {0}, word = {0};
"""

TYPE_USER: Final[TypedDict] = TypedDict(
    "TYPE_USER",
    {
        "discord_user_id": int,
        "name": str,
        "voice": str,
    },
)
TYPE_WORD: Final[TypedDict] = TypedDict(
    "TYPE_WORD",
    {
        "word_id": int,
        "discord_server_id": str,
        "word": str,
        "reading": str,
    },
)
TYPE_VOICE_CATEGORY: Final[TypedDict] = TypedDict(
    "TYPE_VOICE_CATEGORY",
    {
        "voice": str,
        "name": str,
        "message": str,
    },
)
TYPE_SYSTEM_MESSAGES: Final[TypedDict] = TypedDict(
    "TYPE_SYSTEM_MESSAGES",
    {
        "SUMMON_SUCCESS": str,
        "SUMMON_FAILURE": str,
        "BYE_SUCCESS": str,
        "BYE_FAILURE": str,
        "WELCOME": str,
        "FAREWELL": str,
        "CHANGE_FAILURE": str,
    },
)
