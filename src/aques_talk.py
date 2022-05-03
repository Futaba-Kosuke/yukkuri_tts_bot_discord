import re
import subprocess
from dataclasses import dataclass, field
from typing import Final, List, Optional

from abstracts import AbstractVoiceGenerator
from commons import TYPE_SYSTEM_MESSAGES, TYPE_VOICE_CATEGORY

URL_PATTERN: Final[str] = r"https?://[\w/:%#\$&\?\(\)~\.=\+\-]+"

MESSAGE_SUMMON_SUCCESS: Final[str] = "ゆっくりしていってね！"
MESSAGE_SUMMON_FAILURE: Final[str] = "ボイスチャンネルに入ってから話しかけてね！"
MESSAGE_BYE_SUCCESS: Final[str] = "また呼んでね！"
MESSAGE_BYE_FAILURE: Final[str] = "ボイスチャンネルに入ってないよ！"
MESSAGE_WELCOME: Final[str] = "{}さん、いらっしゃい。ゆっくりしていってね！"
MESSAGE_FAREWELL: Final[str] = "{}さん、さようなら。また来てね！"
MESSAGE_CHANGE_SUCCESS_REIMU: Final[str] = "ゆっくり霊夢よ。{}さんのコメントは私が読み上げさせて貰うわね。"
MESSAGE_CHANGE_SUCCESS_MARISA: Final[str] = "ゆっくり魔理沙だぜ。{}さんのコメントは私が読み上げさせて貰うぜ。"
MESSAGE_CHANGE_FAILURE: Final[str] = "読み上げは `霊夢` か `魔理沙` のどちらかに頼んでね！"

VOICE_CATEGORIES: Final[List[TYPE_VOICE_CATEGORY]] = [
    {
        "voice": "f1",
        "name": "霊夢",
        "message": MESSAGE_CHANGE_SUCCESS_REIMU,
    },
    {
        "voice": "f2",
        "name": "魔理沙",
        "message": MESSAGE_CHANGE_SUCCESS_MARISA,
    },
]
SYSTEM_MESSAGES: Final[TYPE_SYSTEM_MESSAGES] = {
    "SUMMON_SUCCESS": MESSAGE_SUMMON_SUCCESS,
    "SUMMON_FAILURE": MESSAGE_SUMMON_FAILURE,
    "BYE_SUCCESS": MESSAGE_BYE_SUCCESS,
    "BYE_FAILURE": MESSAGE_BYE_FAILURE,
    "WELCOME": MESSAGE_WELCOME,
    "FAREWELL": MESSAGE_FAREWELL,
    "CHANGE_FAILURE": MESSAGE_CHANGE_FAILURE,
}


@dataclass
class AquesTalkGenerator(AbstractVoiceGenerator):
    aques_talk_path: Optional[str]
    voice_categories: List[TYPE_VOICE_CATEGORY] = field(
        init=False, default_factory=list
    )
    system_messages: TYPE_SYSTEM_MESSAGES = field(init=False)

    def __post_init__(self):
        self.voice_categories = VOICE_CATEGORIES
        self.system_messages = SYSTEM_MESSAGES

    def generate(
        self, destination_path: str, message: str, voice: str
    ) -> None:
        message_clean = self.preprocess_message(message=message)
        subprocess.run(
            f"{self.aques_talk_path} -v {voice} '{message_clean}' > {destination_path}",  # noqa: E501
            shell=True,
        )

    def preprocess_message(self, message: str) -> str:
        if re.match(URL_PATTERN, message):
            return "URL省略"
        message = message.replace("'", "")
        message = message[:40]
        return message

    def get_voice_categories(self) -> List[TYPE_VOICE_CATEGORY]:
        return self.voice_categories

    def get_system_messages(self) -> TYPE_SYSTEM_MESSAGES:
        return self.system_messages
