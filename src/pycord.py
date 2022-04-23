import asyncio
from typing import Any, Optional

import discord
from constants import (
    BYE_FAILURE_MESSAGE,
    BYE_SUCCESS_MESSAGE,
    COMMAND_PREFIX,
    SUMMON_FAILURE_MESSAGE,
    SUMMON_SUCCESS_MESSAGE,
)
from discord import VoiceChannel
from discord.errors import ClientException
from discord.ext import commands

# ボットの定義
bot = commands.Bot(command_prefix=COMMAND_PREFIX)
# ボイスチャンネルの保存先
voiceChannel: Optional[VoiceChannel] = None
sound_file_path: str = "./tmp/{}.raw"
voiceGenerator: Any = None


@bot.event
async def on_ready():
    print("Hello Yukkuri")


@bot.command()
async def connect(context):
    global voiceChannel
    try:
        # 呼び出したユーザの参加しているボイスチャンネルを取得
        target_voice_channel = context.author.voice
        # 接続成功
        if target_voice_channel is not None:
            voiceChannel = await target_voice_channel.channel.connect()
            await context.channel.send(SUMMON_SUCCESS_MESSAGE)
        # 接続失敗
        else:
            await context.channel.send(SUMMON_FAILURE_MESSAGE)
    except ClientException:
        voiceChannel = None
    return


@bot.command()
async def disconnect(context):
    global voiceChannel
    try:
        # 切断
        if voiceChannel is not None:
            await context.channel.send(BYE_SUCCESS_MESSAGE)
            await voiceChannel.disconnect()
        else:
            await context.channel.send(BYE_FAILURE_MESSAGE)
    finally:
        voiceChannel = None
    return


@bot.listen()
async def on_message(message):
    # ボットからのメッセージを無視
    if message.author.bot or voiceChannel is None:
        return

    # ファイル名用のサーバIDを取得
    server_id: str = message.guild.id

    # 再生中の場合、待機
    while voiceChannel.is_playing():
        await asyncio.sleep(1)

    voiceGenerator.generate(
        destination_path=sound_file_path.format(server_id),
        message=message.content,
    )
    voiceChannel.play(
        discord.FFmpegPCMAudio(sound_file_path.format(server_id))
    )

    return


def run(token: str, voiceGeneratorArg: Any, sound_file_path_arg: str) -> None:
    global voiceGenerator
    global sound_file_path
    voiceGenerator = voiceGeneratorArg
    sound_file_path = sound_file_path_arg

    bot.run(token)
