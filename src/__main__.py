import os
from typing import Final, Optional

from dotenv import load_dotenv

from abstracts import AbstractSqlClient, AbstractVoiceGenerator
from aques_talk import AquesTalkGenerator as VoiceGenerator
from constants import DB_NAME
from pycord import run
from sqlite_client import SqliteClient as SqlClient

load_dotenv()
DISCORD_ACCESS_TOKEN: Final[Optional[str]] = os.getenv("DISCORD_ACCESS_TOKEN")
AQUES_TALK_PATH: Final[Optional[str]] = os.getenv("AQUES_TALK_PATH")


def main() -> None:
    if DISCORD_ACCESS_TOKEN is not None:
        voice_generator: AbstractVoiceGenerator = VoiceGenerator(
            aques_talk_path=AQUES_TALK_PATH
        )
        sql_client: AbstractSqlClient = SqlClient(db_name=DB_NAME)
        run(
            token=DISCORD_ACCESS_TOKEN,
            voice_generator_=voice_generator,
            sql_client_=sql_client,
            sound_file_path_="./tmp/{}.raw",
        )


if __name__ == "__main__":
    main()
