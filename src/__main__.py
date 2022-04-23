import os
from typing import Final, Optional

from dotenv import load_dotenv

from discord_client.pycord import run

load_dotenv()
DISCORD_ACCESS_TOKEN: Final[Optional[str]] = os.getenv("DISCORD_ACCESS_TOKEN")


def main() -> None:
    if DISCORD_ACCESS_TOKEN is not None:
        run(token=DISCORD_ACCESS_TOKEN)


if __name__ == "__main__":
    main()
