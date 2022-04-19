from discord.channel import VoiceChannel
from discord.ext import commands

from constants import (
    BYE_SUCCESS_MESSAGE,
    COMMAND_PREFIX,
    SUMMON_FAILURE_MESSAGE,
    SUMMON_SUCCESS_MESSAGE,
)

# ボットの定義
bot = commands.Bot(command_prefix=COMMAND_PREFIX)
# ボイスチャンネルの保存先
voiceChannel: VoiceChannel


@bot.event
async def on_ready():
    print("Hello Yukkuri")


@bot.command()
async def connect(context):
    global voiceChannel
    # 呼び出したユーザの参加しているボイスチャンネルを取得
    target_voice_channel = context.author.voice
    # 接続成功
    if target_voice_channel is not None:
        voiceChannel = await target_voice_channel.channel.connect()
        await context.channel.send(SUMMON_SUCCESS_MESSAGE)
    # 接続失敗
    else:
        await context.channel.send(SUMMON_FAILURE_MESSAGE)
    return


@bot.command()
async def disconnect(context):
    global voiceChannel
    await context.channel.send(BYE_SUCCESS_MESSAGE)
    await voiceChannel.disconnect()
    return


@bot.listen()
async def on_message(message):
    if message.author.bot:
        return
    return


def run(token: str) -> None:
    bot.run(token)
