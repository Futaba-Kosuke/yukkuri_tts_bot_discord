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
    "TYPE_USER",
    {
        "discord_user_id": int,
        "name": str,
        "voice": str,
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
