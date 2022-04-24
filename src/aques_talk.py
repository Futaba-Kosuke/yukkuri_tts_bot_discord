import os
import subprocess
from dataclasses import dataclass
from typing import Final, Optional

from dotenv import load_dotenv

load_dotenv()

AQUES_TALK_PATH: Final[Optional[str]] = os.getenv("AQUES_TALK_PATH")


@dataclass
class AquesTalkGenerator:
    def generate(self, destination_path: str, message: str):
        message_clean = message.replace("'", "")
        subprocess.run(
            f"{AQUES_TALK_PATH} '{message_clean}' > {destination_path}",  # noqa
            shell=True,
        )
