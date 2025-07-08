import asyncio
import os
import re
from typing import Dict, Final, List, Optional

import discord
from discord import TextChannel, VoiceClient
from discord.ext import commands
from dotenv import load_dotenv

from abstracts import AbstractSqlClient, AbstractVoiceGenerator
from commons import (
    TYPE_DICTIONARY,
    TYPE_SYSTEM_MESSAGES,
    TYPE_USER,
    TYPE_VOICE_CATEGORY,
)

load_dotenv()

OPUS_PATH: Optional[str] = os.getenv("OPUS_PATH")
discord.opus.load_opus(OPUS_PATH)

GUILD_IDS_RAW: Optional[str] = os.getenv("GUILD_IDS")
GUILD_IDS: Final[List[int]] = (
    [int(x) for x in GUILD_IDS_RAW.split(",")] if GUILD_IDS_RAW else []
)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

voice_clients: Dict[str, Optional[VoiceClient]] = {}
text_channels: Dict[str, Optional[TextChannel]] = {}
sound_file_path: str
voice_generator: AbstractVoiceGenerator
sql_client: AbstractSqlClient
voice_categories: List[TYPE_VOICE_CATEGORY]
system_messages: TYPE_SYSTEM_MESSAGES
guild_ids: List[int]

@bot.event
async def on_ready():
    print("Hello Yukkuri")
    try:
        # 明示的にguildごとにコマンド同期
        for gid in GUILD_IDS:
            guild = discord.Object(id=gid)
            await tree.sync(guild=guild)
        print("Slash commands synced!")
    except Exception as e:
        print(f"Sync Error: {e}")

@bot.event
async def on_voice_state_update(member, before, after) -> None:
    global voice_clients
    global text_channels

    server_id = str(member.guild.id)
    name = member.display_name
    voice_client = voice_clients.get(server_id)
    text_channel = text_channels.get(server_id)

    if voice_client is None or text_channel is None:
        return

    if before.channel != after.channel:
        if member.id == bot.user.id:
            return

        if before.channel is None:
            message = system_messages["WELCOME"].format(name)
            await text_channel.send(message)
            await play_voice(
                message=message,
                server_id=server_id,
                discord_user_id=None,
            )
        if after.channel is None:
            message = system_messages["FAREWELL"].format(name)
            await text_channel.send(message)
            await play_voice(
                message=message,
                server_id=server_id,
                discord_user_id=None,
            )

        if len(voice_client.channel.voice_states.keys()) == 1:
            await voice_client.disconnect()
            voice_clients[server_id] = None
            text_channels[server_id] = None

# --- スラッシュコマンド群 ---

def get_guild_obj_list():
    return [discord.Object(id=gid) for gid in GUILD_IDS]

@tree.command(name="connect", description="ボイスチャンネルに接続します", guilds=get_guild_obj_list())
async def connect(interaction: discord.Interaction):
    global voice_clients

    server_id: str = str(interaction.guild.id)
    author = interaction.user
    target_voice = author.voice

    if target_voice is not None:
        voice_clients[server_id] = await target_voice.channel.connect()
        text_channels[server_id] = interaction.channel
        await interaction.response.send_message(system_messages["SUMMON_SUCCESS"])
        await play_voice(
            message=system_messages["SUMMON_SUCCESS"],
            server_id=server_id,
            discord_user_id=None,
        )
    else:
        await interaction.response.send_message(system_messages["SUMMON_FAILURE"])

@tree.command(name="disconnect", description="ボイスチャンネルから切断します", guilds=get_guild_obj_list())
async def disconnect(interaction: discord.Interaction):
    global voice_clients

    server_id: str = str(interaction.guild.id)
    voice_client = voice_clients.get(server_id)

    if voice_client is not None:
        await interaction.response.send_message(system_messages["BYE_SUCCESS"])
        await voice_client.disconnect()
        voice_clients[server_id] = None
        text_channels[server_id] = None
    else:
        await interaction.response.send_message(system_messages["BYE_FAILURE"])

@tree.command(name="change", description="声を変更します", guilds=get_guild_obj_list())
@discord.app_commands.describe(voice_name="声の名前")
async def change(interaction: discord.Interaction, voice_name: str):
    discord_user_id: int = interaction.user.id
    display_name: str = interaction.user.display_name
    server_id: str = str(interaction.guild.id)

    voice_categories_filtered: List[TYPE_VOICE_CATEGORY] = [
        voice_category
        for voice_category in voice_categories
        if voice_category["name"] == voice_name
    ]
    if len(voice_categories_filtered) == 0:
        await interaction.response.send_message(system_messages["CHANGE_FAILURE"])
        return

    voice_category: TYPE_VOICE_CATEGORY = voice_categories_filtered[0]
    voice: str = voice_category["voice"]

    user: TYPE_USER = sql_client.select_user(discord_user_id)

    if user is None:
        sql_client.insert_user(
            discord_user_id=discord_user_id, name=display_name, voice=voice
        )
    else:
        sql_client.update_user(
            discord_user_id=discord_user_id, name=display_name, voice=voice
        )

    message: str = voice_category["message"].format(display_name)
    await interaction.response.send_message(message)
    await play_voice(
        message=message,
        server_id=server_id,
        discord_user_id=discord_user_id,
    )

@tree.command(name="dictionary", description="辞書を登録・更新します", guilds=get_guild_obj_list())
@discord.app_commands.describe(word="単語", reading="読み")
async def dictionary(interaction: discord.Interaction, word: str, reading: str):
    server_id: str = str(interaction.guild.id)

    target_dictionary = sql_client.select_dictionary(
        discord_server_id=server_id, word=word
    )

    if target_dictionary is None:
        sql_client.insert_dictionary(
            discord_server_id=server_id, word=word, reading=reading
        )
    else:
        sql_client.update_dictionary(
            discord_server_id=server_id, word=word, reading=reading
        )

    message: str = system_messages["DICTIONARY_SUCCESS"].format(word, reading)
    await interaction.response.send_message(message)
    await play_voice(
        message=message,
        server_id=server_id,
        discord_user_id=None,
    )

@tree.command(name="delete_dictionary", description="辞書から単語を削除します", guilds=get_guild_obj_list())
@discord.app_commands.describe(word="単語")
async def delete_dictionary(interaction: discord.Interaction, word: str):
    server_id: str = str(interaction.guild.id)

    target_dictionary = sql_client.select_dictionary(
        discord_server_id=server_id, word=word
    )

    if target_dictionary is None:
        message = system_messages["DELETE_DICTIONARY_FAILURE"].format(word)
        await interaction.response.send_message(message)
        await play_voice(
            message=message,
            server_id=server_id,
            discord_user_id=None,
        )
        return

    sql_client.delete_dictionary(discord_server_id=server_id, word=word)

    message = system_messages["DELETE_DICTIONARY_SUCCESS"].format(word)
    await interaction.response.send_message(message)
    await play_voice(
        message=message,
        server_id=server_id,
        discord_user_id=None,
    )

@bot.event
async def on_message(message) -> None:
    # スラッシュコマンドはon_messageで無視されるため、手動で処理する必要はありません
    server_id: str = str(message.guild.id)
    text_channel = text_channels.get(server_id)
    discord_user_id: int = message.author.id

    if (
        message.author.bot
        or text_channel is None
        or message.content.startswith("/")
        or text_channel.id != message.channel.id
    ):
        await bot.process_commands(message)
        return

    dictionaries: List[TYPE_DICTIONARY] = sql_client.select_dictionaries(
        discord_server_id=server_id
    )

    msg = replace_dictionaries(
        message=message.clean_content, dictionaries=dictionaries
    )
    await play_voice(
        message=msg, server_id=server_id, discord_user_id=discord_user_id
    )

    await bot.process_commands(message)

def replace_dictionaries(
    message: str, dictionaries: List[TYPE_DICTIONARY]
) -> str:
    translate_dict = {
        dictionary["word"]: dictionary["reading"]
        for dictionary in dictionaries
    }
    if translate_dict:
        return re.sub(
            "({})".format("|".join(map(re.escape, translate_dict.keys()))),
            lambda m: translate_dict[m.group()],
            message,
        )
    else:
        return message

async def play_voice(
    message: str, server_id: str, discord_user_id: Optional[int]
) -> None:
    voice_client = voice_clients.get(server_id)
    if voice_client is None:
        return

    voice = get_voice(discord_user_id=discord_user_id)

    while voice_client.is_playing():
        await asyncio.sleep(1)

    voice_generator.generate(
        destination_path=sound_file_path.format(server_id),
        message=message,
        voice=voice,
    )
    voice_client.play(
        discord.FFmpegPCMAudio(sound_file_path.format(server_id))
    )

def get_voice(discord_user_id: Optional[int]) -> str:
    if discord_user_id is None:
        voice = voice_categories[0]["voice"]
    else:
        user: TYPE_USER = sql_client.select_user(
            discord_user_id=discord_user_id
        )
        if user is None:
            voice = voice_categories[0]["voice"]
        elif not user.get("voice") in [
            voice_category["voice"] for voice_category in voice_categories
        ]:
            voice = voice_categories[0]["voice"]
        else:
            voice = user["voice"]
    return voice

def run(
    token: str,
    voice_generator_: AbstractVoiceGenerator,
    sql_client_: AbstractSqlClient,
    sound_file_path_: str,
) -> None:
    global voice_generator
    global voice_categories
    global system_messages
    global sql_client
    global sound_file_path

    voice_generator = voice_generator_
    voice_categories = voice_generator.get_voice_categories()
    system_messages = voice_generator.get_system_messages()
    sql_client = sql_client_
    sound_file_path = sound_file_path_

    bot.run(token)