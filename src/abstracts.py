from abc import ABCMeta, abstractmethod
from typing import List

from commons import (
    TYPE_DICTIONARY,
    TYPE_SYSTEM_MESSAGES,
    TYPE_USER,
    TYPE_VOICE_CATEGORY,
)


class AbstractVoiceGenerator(metaclass=ABCMeta):
    @abstractmethod
    def generate(
        self, destination_path: str, message: str, voice: str
    ) -> None:
        return

    @abstractmethod
    def preprocess_message(self, message: str) -> str:
        return "message"

    @abstractmethod
    def get_voice_categories(self) -> List[TYPE_VOICE_CATEGORY]:
        return [
            {
                "voice": "voice",
                "name": "name",
                "message": "message",
            }
        ]

    @abstractmethod
    def get_system_messages(self) -> TYPE_SYSTEM_MESSAGES:
        return {
            "SUMMON_SUCCESS": "str",
            "SUMMON_FAILURE": "str",
            "BYE_SUCCESS": "str",
            "BYE_FAILURE": "str",
            "WELCOME": "str",
            "FAREWELL": "str",
            "CHANGE_FAILURE": "str",
            "DICTIONARY_SUCCESS": "str",
            "DELETE_DICTIONARY_SUCCESS": "str",
            "DELETE_DICTIONARY_FAILURE": "str",
        }


class AbstractSqlClient(metaclass=ABCMeta):
    @abstractmethod
    def insert_user(self, discord_user_id: int, name: str, voice: str) -> None:
        return

    @abstractmethod
    def select_user(self, discord_user_id: int) -> TYPE_USER:
        return {
            "discord_user_id": 0,
            "name": "test",
            "voice": "0",
        }

    @abstractmethod
    def update_user(self, discord_user_id: int, name: str, voice: str) -> None:
        return

    @abstractmethod
    def insert_dictionary(
        self, discord_server_id: str, word: str, reading: str
    ) -> None:
        return

    @abstractmethod
    def select_dictionary(
        self, discord_server_id: str, word: str
    ) -> TYPE_DICTIONARY:
        return {
            "dictionary_id": 0,
            "discord_server_id": "discord_server_id",
            "word": "テスト",
            "reading": "てすと",
        }

    @abstractmethod
    def select_dictionaries(
        self, discord_server_id: str
    ) -> List[TYPE_DICTIONARY]:
        return [
            {
                "dictionary_id": 0,
                "discord_server_id": "discord_server_id",
                "word": "テスト",
                "reading": "てすと",
            }
        ]

    @abstractmethod
    def update_dictionary(
        self, discord_server_id: str, word: str, reading: str
    ) -> None:
        return

    @abstractmethod
    def delete_dictionary(self, discord_server_id: str, word: str) -> None:
        return
