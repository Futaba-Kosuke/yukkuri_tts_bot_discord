import asyncio
from typing import Any, Dict, Optional

import discord
from discord import VoiceChannel
from discord.ext import commands

from constants import (
    BYE_FAILURE_MESSAGE,
    BYE_SUCCESS_MESSAGE,
    COMMAND_PREFIX,
    SUMMON_FAILURE_MESSAGE,
    SUMMON_SUCCESS_MESSAGE,
)

# ボットの定義
bot = commands.Bot(command_prefix=COMMAND_PREFIX)
# ボイスチャンネルの保存先
voiceChannels: Dict[str, Optional[VoiceChannel]] = {}
sound_file_path: str = "./tmp/{}.raw"
voiceGenerator: Any = None


@bot.event
async def on_ready():
    print("Hello Yukkuri")


@bot.command()
async def connect(context):
    global voiceChannels

    # サーバIDを取得
    server_id: str = context.guild.id

    # 呼び出したユーザの参加しているボイスチャンネルを取得
    target_voice_channel = context.author.voice
    # 接続成功
    if target_voice_channel is not None:
        voiceChannels[server_id] = await target_voice_channel.channel.connect()
        await context.channel.send(SUMMON_SUCCESS_MESSAGE)
        play_voice(message=SUMMON_SUCCESS_MESSAGE, server_id=server_id)
    # 接続失敗
    else:
        await context.channel.send(SUMMON_FAILURE_MESSAGE)
    return


@bot.command()
async def disconnect(context):
    global voiceChannels

    # サーバIDを取得
    server_id: str = context.guild.id

    # 切断
    if voiceChannels.get(server_id) is not None:
        await context.channel.send(BYE_SUCCESS_MESSAGE)
        await voiceChannels.get(server_id).disconnect()
    else:
        await context.channel.send(BYE_FAILURE_MESSAGE)

    return


@bot.listen()
async def on_message(message):

    # サーバIDを取得
    server_id: str = message.guild.id

    # ボットからのメッセージ, ボイスチャンネルが未定義, コマンドのとき無視
    if (
        message.author.bot
        or voiceChannels.get(server_id) is None
        or message.content.startswith(COMMAND_PREFIX)
    ):
        return

    # 再生中の場合、待機
    while voiceChannels.get(server_id).is_playing():
        await asyncio.sleep(1)

    play_voice(message=message.content, server_id=server_id)

    return


def play_voice(message: str, server_id: str):
    # ボイスチャンネルが未定義のとき無視
    voiceChannel = voiceChannels.get(server_id)
    if voiceChannel is None:
        return

    voiceGenerator.generate(
        destination_path=sound_file_path.format(server_id),
        message=message,
    )
    voiceChannel.play(
        discord.FFmpegPCMAudio(sound_file_path.format(server_id))
    )


def run(token: str, voiceGeneratorArg: Any, sound_file_path_arg: str) -> None:
    global voiceGenerator
    global sound_file_path
    voiceGenerator = voiceGeneratorArg
    sound_file_path = sound_file_path_arg

    bot.run(token)
