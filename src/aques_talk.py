import re
import subprocess
from dataclasses import dataclass
from typing import Final, Optional

from abstracts import AbstractVoiceGenerator

URL_PATTERN: Final[str] = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"


@dataclass
class AquesTalkGenerator(AbstractVoiceGenerator):
    aques_talk_path: Optional[str]

    def generate(self, destination_path: str, message: str) -> None:
        message_clean = self.preprocess_message(message=message)
        subprocess.run(
            f"{self.aques_talk_path} '{message_clean}' > {destination_path}",
            shell=True,
        )

    def preprocess_message(self, message: str) -> str:
        if re.match(URL_PATTERN, message):
            return "URL省略"
        message = message.replace("'", "")
        message = message[:40]
        return message
