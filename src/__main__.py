import os
from typing import Final, Optional

from dotenv import load_dotenv

from aques_talk import AquesTalkGenerator as VoiceGenerator
from pycord import run

load_dotenv()
DISCORD_ACCESS_TOKEN: Final[Optional[str]] = os.getenv("DISCORD_ACCESS_TOKEN")
AQUES_TALK_PATH: Final[Optional[str]] = os.getenv("AQUES_TALK_PATH")


def main() -> None:
    if DISCORD_ACCESS_TOKEN is not None:
        voiceGenerator = VoiceGenerator(aques_talk_path=AQUES_TALK_PATH)
        run(
            token=DISCORD_ACCESS_TOKEN,
            voiceGeneratorArg=voiceGenerator,
            sound_file_path_arg="./tmp/{}.raw",
        )


if __name__ == "__main__":
    main()
