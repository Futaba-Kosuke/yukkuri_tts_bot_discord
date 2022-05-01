import asyncio
from typing import Any, Dict, Optional

import discord
from discord import TextChannel, VoiceClient
from discord.ext import commands

from constants import (
    BYE_FAILURE_MESSAGE,
    BYE_SUCCESS_MESSAGE,
    COMMAND_PREFIX,
    FAREWELL_MESSAGE,
    SUMMON_FAILURE_MESSAGE,
    SUMMON_SUCCESS_MESSAGE,
    WELCOME_MESSAGE,
)

# ボットの定義
bot = commands.Bot(command_prefix=COMMAND_PREFIX)
# ボイスチャンネルの保存先
voiceClients: Dict[str, Optional[VoiceClient]] = {}
textChannels: Dict[str, Optional[TextChannel]] = {}
sound_file_path: str = "./tmp/{}.raw"
voiceGenerator: Any = None


# ボットの起動
@bot.event
async def on_ready():
    print("Hello Yukkuri")


# ボイスチャンネルの状態変更
@bot.event
async def on_voice_state_update(member, before, after) -> None:
    global voiceClients
    global textChannels

    # サーバIDを取得
    server_id = member.guild.id
    # 入退室者の名前の取得
    name = member.name
    # ボイスクライアント・テキストチャンネルを取得
    voiceClient = voiceClients.get(server_id)
    textChannel = textChannels.get(server_id)

    # ボイスチャンネルに入室していないとき、無視
    if voiceClient is None or textChannel is None:
        return

    # メンバーの入退室時
    if before.channel != after.channel:

        # ボット自身の入退室の場合
        if member.id == bot.user.id:
            return

        # メンバーの入室時
        if before.channel is None:
            message = WELCOME_MESSAGE.format(name)
            await textChannel.send(message)
            play_voice(message=message, server_id=server_id)

        # メンバーの退出時
        if after.channel is None:
            message = FAREWELL_MESSAGE.format(name)
            await textChannel.send(message)
            play_voice(message=message, server_id=server_id)

        # 誰も居なくなった時に自動で退出
        if len(voiceClient.channel.voice_states.keys()) == 1:
            await voiceClient.disconnect()


@bot.command()
async def connect(context) -> None:
    global voiceClients

    # サーバIDを取得
    server_id: str = context.guild.id

    # 呼び出したユーザの参加しているボイスチャンネルを取得
    target_voice_channel = context.author.voice
    # 接続成功
    if target_voice_channel is not None:
        voiceClients[server_id] = await target_voice_channel.channel.connect()
        textChannels[server_id] = context.channel
        await context.channel.send(SUMMON_SUCCESS_MESSAGE)
        play_voice(message=SUMMON_SUCCESS_MESSAGE, server_id=server_id)
    # 接続失敗
    else:
        await context.channel.send(SUMMON_FAILURE_MESSAGE)
    return


@bot.command()
async def disconnect(context) -> None:
    global voiceClients

    # サーバIDを取得
    server_id: str = context.guild.id
    # ボイスクライアント・テキストチャンネルを取得
    voiceClient = voiceClients.get(server_id)

    # 切断
    if voiceClient is not None:
        await context.channel.send(BYE_SUCCESS_MESSAGE)
        await voiceClient.disconnect()
        voiceClients[server_id] = None
        textChannels[server_id] = None
    else:
        await context.channel.send(BYE_FAILURE_MESSAGE)

    return


@bot.listen()
async def on_message(context) -> None:

    # サーバIDを取得
    server_id: str = context.guild.id
    # ボイスクライアント・テキストチャンネルを取得
    voiceClient = voiceClients.get(server_id)
    textChannel = textChannels.get(server_id)

    # ボットからのメッセージ, ボイスチャンネルが未定義, コマンドのとき無視
    if (
        context.author.bot
        or voiceClient is None
        or textChannel is None
        or context.content.startswith(COMMAND_PREFIX)
        or textChannel.id != context.channel.id
    ):
        return

    # 再生中の場合、待機
    while voiceClient.is_playing():
        await asyncio.sleep(1)

    message = context.content
    play_voice(message=message, server_id=server_id)

    return


def play_voice(message: str, server_id: str) -> None:
    # ボイスチャンネルが未定義のとき無視
    voiceClient = voiceClients.get(server_id)
    if voiceClient is None:
        return

    voiceGenerator.generate(
        destination_path=sound_file_path.format(server_id),
        message=message,
    )
    voiceClient.play(discord.FFmpegPCMAudio(sound_file_path.format(server_id)))


def run(token: str, voiceGeneratorArg: Any, sound_file_path_arg: str) -> None:
    global voiceGenerator
    global sound_file_path
    voiceGenerator = voiceGeneratorArg
    sound_file_path = sound_file_path_arg

    bot.run(token)
