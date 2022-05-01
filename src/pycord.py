import asyncio
from typing import Dict, Optional

import discord
from discord import TextChannel, VoiceClient
from discord.ext import commands

from abstracts import AbstractSqlClient, AbstractVoiceGenerator
from constants import (
    BYE_FAILURE_MESSAGE,
    BYE_SUCCESS_MESSAGE,
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


# ボイスチャンネルの状態変更
@bot.event
async def on_voice_state_update(member, before, after) -> None:
    global voice_clients
    global text_channels

    # サーバIDを取得
    server_id = member.guild.id
    # 入退室者の名前の取得
    name = member.name
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
            play_voice(message=message, server_id=server_id)

        # メンバーの退出時
        if after.channel is None:
            message = FAREWELL_MESSAGE.format(name)
            await text_channel.send(message)
            play_voice(message=message, server_id=server_id)

        # 誰も居なくなった時に自動で退出
        if len(voice_client.channel.voice_states.keys()) == 1:
            await voice_client.disconnect()
            voice_clients[server_id] = None
            text_channels[server_id] = None


@bot.command()
async def connect(context) -> None:
    global voice_clients

    # サーバIDを取得
    server_id: str = context.guild.id

    # 呼び出したユーザの参加しているボイスチャンネルを取得
    target_voice_channel = context.author.voice
    # 接続成功
    if target_voice_channel is not None:
        voice_clients[server_id] = await target_voice_channel.channel.connect()
        text_channels[server_id] = context.channel
        await context.channel.send(SUMMON_SUCCESS_MESSAGE)
        play_voice(message=SUMMON_SUCCESS_MESSAGE, server_id=server_id)
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


@bot.listen()
async def on_message(context) -> None:
    # サーバIDを取得
    server_id: str = context.guild.id
    # ボイスクライアント・テキストチャンネルを取得
    voice_client = voice_clients.get(server_id)
    text_channel = text_channels.get(server_id)

    # ボットからのメッセージ, ボイスチャンネルが未定義, コマンドのとき無視
    if (
        context.author.bot
        or voice_client is None
        or text_channel is None
        or context.content.startswith(COMMAND_PREFIX)
        or text_channel.id != context.channel.id
    ):
        return

    # 再生中の場合、待機
    while voice_client.is_playing():
        await asyncio.sleep(1)

    message = context.content
    play_voice(message=message, server_id=server_id)

    return


def play_voice(message: str, server_id: str) -> None:
    # ボイスチャンネルが未定義のとき無視
    voice_client = voice_clients.get(server_id)
    if voice_client is None:
        return

    voice_generator.generate(
        destination_path=sound_file_path.format(server_id),
        message=message,
    )
    voice_client.play(
        discord.FFmpegPCMAudio(sound_file_path.format(server_id))
    )


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
