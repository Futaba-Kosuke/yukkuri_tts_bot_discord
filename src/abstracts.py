from abc import ABCMeta, abstractmethod

from constants import TYPE_USER


class AbstractVoiceGenerator(metaclass=ABCMeta):
    @abstractmethod
    def generate(self, destination_path: str, message: str) -> None:
        return

    @abstractmethod
    def preprocess_message(self, message: str) -> str:
        return "message"


class AbstractSqlClient(metaclass=ABCMeta):
    @abstractmethod
    def insert_user(self, discord_user_id: int, name: str, voice: str) -> None:
        return

    @abstractmethod
    def select_user_from_discord_user_id(
        self, discord_user_id: int
    ) -> TYPE_USER:
        return {"discord_user_id": 0, "name": "test", "voice": "0"}

    @abstractmethod
    def update_user_from_discord_user_id(
        self, discord_user_id: int, name: str, voice: str
    ) -> None:
        return
