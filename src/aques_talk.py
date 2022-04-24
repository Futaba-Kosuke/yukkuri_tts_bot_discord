import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class AquesTalkGenerator:
    aques_talk_path: Optional[str]

    def generate(self, destination_path: str, message: str):
        message_clean = message.replace("'", "")
        subprocess.run(
            f"{self.aques_talk_path} '{message_clean}' > {destination_path}",
            shell=True,
        )
