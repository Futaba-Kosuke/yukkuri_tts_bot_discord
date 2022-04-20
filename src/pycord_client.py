from discord.errors import ClientException
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
voiceChannel = None


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
    if message.author.bot:
        return
    return


def run(token: str) -> None:
    bot.run(token)
