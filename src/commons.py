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
QUERY_CREATE_DICTIONARY_TABLE: Final[
    str
] = """
CREATE TABLE IF NOT EXISTS dictionaries (
    dictionary_id INTEGER PRIMARY KEY AUTOINCREMENT,
    discord_server_id VARCHAR,
    word VARCHAR,
    reading VARCHAR
);
"""
QUERY_INSERT_DICTIONARY: Final[
    str
] = """
INSERT INTO dictionaries(discord_server_id, word, reading)
values({0}, {0}, {0});
"""
QUERY_SELECT_DICTIONARY: Final[
    str
] = """
SELECT * FROM dictionaries WHERE discord_server_id = {0} AND word = {0};
"""
QUERY_SELECT_DICTIONARIES: Final[
    str
] = """
SELECT * FROM dictionaries WHERE discord_server_id = {0};
"""
QUERY_UPDATE_DICTIONARY: Final[
    str
] = """
UPDATE dictionaries SET reading = {0}
WHERE discord_server_id = {0} AND word = {0};
"""

TYPE_USER: Final[TypedDict] = TypedDict(
    "TYPE_USER",
    {
        "discord_user_id": int,
        "name": str,
        "voice": str,
    },
)
TYPE_DICTIONARY: Final[TypedDict] = TypedDict(
    "TYPE_DICTIONARY",
    {
        "dictionary_id": int,
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
        "DICTIONARY_SUCCESS": str,
    },
)
