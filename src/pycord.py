import asyncio
from typing import Dict, Optional

import discord
from discord import TextChannel, VoiceClient
from discord.ext import commands

from abstracts import AbstractSqlClient, AbstractVoiceGenerator
from constants import (
    BYE_FAILURE_MESSAGE,
    BYE_SUCCESS_MESSAGE,
    CHANGE_FAILURE_MESSAGE,
    CHANGE_SUCCESS_MARISA_MESSAGE,
    CHANGE_SUCCESS_REIMU_MESSAGE,
    COMMAND_PREFIX,
    FAREWELL_MESSAGE,
    SUMMON_FAILURE_MESSAGE,
    SUMMON_SUCCESS_MESSAGE,
    TYPE_USER,
    WELCOME_MESSAGE,
)

# ボットの定義
bot = commands.Bot(command_prefix=COMMAND_PREFIX)
# ボイスチャンネルの保存先
voice_clients: Dict[str, Optional[VoiceClient]] = {}
text_channels: Dict[str, Optional[TextChannel]] = {}
sound_file_path: str = "./tmp/{}.raw"
voice_generator: AbstractVoiceGenerator
sql_client: AbstractSqlClient


# ボットの起動
@bot.event
async def on_ready():
    print("Hello Yukkuri")
    return


# ボイスチャンネルの状態変更
@bot.event
async def on_voice_state_update(member, before, after) -> None:
    global voice_clients
    global text_channels

    # サーバIDを取得
    server_id = member.guild.id
    # 入退室者の名前の取得
    name = member.display_name
    # ユーザのIDを取得
    discord_user_id: int = member.id
    # ボイスクライアント・テキストチャンネルを取得
    voice_client = voice_clients.get(server_id)
    text_channel = text_channels.get(server_id)

    # ボイスチャンネルに入室していないとき、無視
    if voice_client is None or text_channel is None:
        return

    # メンバーの入退室時
    if before.channel != after.channel:

        # ボット自身の入退室の場合
        if member.id == bot.user.id:
            return

        # メンバーの入室時
        if before.channel is None:
            message = WELCOME_MESSAGE.format(name)
            await text_channel.send(message)
            await play_voice(
                message=message,
                server_id=server_id,
                discord_user_id=discord_user_id,
            )

        # メンバーの退出時
        if after.channel is None:
            message = FAREWELL_MESSAGE.format(name)
            await text_channel.send(message)
            await play_voice(
                message=message,
                server_id=server_id,
                discord_user_id=discord_user_id,
            )

        # 誰も居なくなった時に自動で退出
        if len(voice_client.channel.voice_states.keys()) == 1:
            await voice_client.disconnect()
            voice_clients[server_id] = None
            text_channels[server_id] = None

    return


@bot.command()
async def connect(context) -> None:
    global voice_clients

    # サーバIDを取得
    server_id: str = context.guild.id
    # ユーザのIDを取得
    discord_user_id: int = context.author.id

    # 呼び出したユーザの参加しているボイスチャンネルを取得
    target_voice_channel = context.author.voice
    # 接続成功
    if target_voice_channel is not None:
        voice_clients[server_id] = await target_voice_channel.channel.connect()
        text_channels[server_id] = context.channel
        await context.channel.send(SUMMON_SUCCESS_MESSAGE)
        await play_voice(
            message=SUMMON_SUCCESS_MESSAGE,
            server_id=server_id,
            discord_user_id=discord_user_id,
        )
    # 接続失敗
    else:
        await context.channel.send(SUMMON_FAILURE_MESSAGE)
    return


@bot.command()
async def disconnect(context) -> None:
    global voice_clients

    # サーバIDを取得
    server_id: str = context.guild.id
    # ボイスクライアント・テキストチャンネルを取得
    voice_client = voice_clients.get(server_id)

    # 切断
    if voice_client is not None:
        await context.channel.send(BYE_SUCCESS_MESSAGE)
        await voice_client.disconnect()
        voice_clients[server_id] = None
        text_channels[server_id] = None
    else:
        await context.channel.send(BYE_FAILURE_MESSAGE)

    return


@bot.command()
async def change(context, voice_type: str) -> None:
    discord_user_id: int = context.author.id
    display_name: str = context.author.display_name
    server_id: str = context.guild.id

    voice: str
    # 成功
    if voice_type == "霊夢":
        await context.channel.send(
            CHANGE_SUCCESS_REIMU_MESSAGE.format(display_name)
        )
        voice = "f1"
    elif voice_type == "魔理沙":
        await context.channel.send(
            CHANGE_SUCCESS_MARISA_MESSAGE.format(display_name)
        )
        voice = "f2"
    # 失敗
    else:
        await context.channel.send(CHANGE_FAILURE_MESSAGE)
        return

    # ユーザをデータベースから検索
    user: TYPE_USER = sql_client.select_user_from_discord_user_id(
        discord_user_id
    )

    # ユーザが存在しない場合
    if user is None:
        sql_client.insert_user(
            discord_user_id=discord_user_id, name=display_name, voice=voice
        )

    # ユーザが存在する場合
    else:
        sql_client.update_user_from_discord_user_id(
            discord_user_id=discord_user_id, name=display_name, voice=voice
        )

    if voice_type == "霊夢":
        await play_voice(
            message=CHANGE_SUCCESS_REIMU_MESSAGE,
            server_id=server_id,
            discord_user_id=discord_user_id,
        )
    elif voice_type == "魔理沙":
        await play_voice(
            message=CHANGE_SUCCESS_MARISA_MESSAGE,
            server_id=server_id,
            discord_user_id=discord_user_id,
        )

    return


@bot.listen()
async def on_message(context) -> None:
    # サーバIDを取得
    server_id: str = context.guild.id
    # テキストチャンネルを取得
    text_channel = text_channels.get(server_id)
    # ユーザのIDを取得
    discord_user_id: int = context.author.id

    # ボットからのメッセージ, ボイスチャンネルが未定義, コマンドのとき無視
    if (
        context.author.bot
        or text_channel is None
        or context.content.startswith(COMMAND_PREFIX)
        or text_channel.id != context.channel.id
    ):
        return

    message = context.content
    await play_voice(
        message=message, server_id=server_id, discord_user_id=discord_user_id
    )

    return


async def play_voice(
    message: str, server_id: str, discord_user_id: int
) -> None:
    # ボイスチャンネルを取得
    voice_client = voice_clients.get(server_id)
    # ボイスチャンネルが未定義のとき無視
    if voice_client is None:
        return

    # 再生する声の取得
    user: TYPE_USER = sql_client.select_user_from_discord_user_id(
        discord_user_id=discord_user_id
    )
    voice: str
    if user is None:
        voice = "f1"
    elif user.get("voice") or not user.get("voice") in ["f1", "f2"]:
        voice = "f1"
    else:
        voice = user["voice"]

    # 再生中の場合、待機
    while voice_client.is_playing():
        await asyncio.sleep(1)

    # 音声を生成
    voice_generator.generate(
        destination_path=sound_file_path.format(server_id),
        message=message,
        voice=voice,
    )
    # 音声を再生
    await voice_client.play(
        discord.FFmpegPCMAudio(sound_file_path.format(server_id))
    )

    return


def run(
    token: str,
    voice_generator_: AbstractVoiceGenerator,
    sql_client_: AbstractSqlClient,
    sound_file_path_: str,
) -> None:
    global voice_generator
    global sql_client
    global sound_file_path

    voice_generator = voice_generator_
    sql_client = sql_client_
    sound_file_path = sound_file_path_

    bot.run(token)

    return
