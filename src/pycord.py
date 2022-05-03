import asyncio
from typing import Dict, List, Optional

import discord
from discord import TextChannel, VoiceClient
from discord.ext import commands

from abstracts import AbstractSqlClient, AbstractVoiceGenerator
from commons import (
    COMMAND_PREFIX,
    TYPE_SYSTEM_MESSAGES,
    TYPE_USER,
    TYPE_VOICE_CATEGORY,
)

# ボットの定義
bot = commands.Bot(command_prefix=COMMAND_PREFIX)
# ボイスチャンネルの保存先
voice_clients: Dict[str, Optional[VoiceClient]] = {}
text_channels: Dict[str, Optional[TextChannel]] = {}
# 音声ファイルの出力・入力先
sound_file_path: str
# 音声の生成器
voice_generator: AbstractVoiceGenerator
# SQL操作器
sql_client: AbstractSqlClient
# 声の種類
voice_categories: List[TYPE_VOICE_CATEGORY]
# システムメッセージ一覧
system_messages: TYPE_SYSTEM_MESSAGES


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
            message = system_messages["WELCOME"].format(name)
            await text_channel.send(message)
            await play_voice(
                message=message,
                server_id=server_id,
                discord_user_id=discord_user_id,
            )

        # メンバーの退出時
        if after.channel is None:
            message = system_messages["FAREWELL"].format(name)
            await text_channel.send(message)
            await play_voice(
                message=message,
                server_id=server_id,
                discord_user_id=discord_user_id,
            )
            print(len(voice_client.channel.voice_states.keys()))

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
    server_id: str = str(context.guild.id)
    # ユーザのIDを取得
    discord_user_id: int = context.author.id

    # 呼び出したユーザの参加しているボイスチャンネルを取得
    target_voice_channel = context.author.voice
    # 接続成功
    if target_voice_channel is not None:
        voice_clients[server_id] = await target_voice_channel.channel.connect()
        text_channels[server_id] = context.channel
        await context.channel.send(system_messages["SUMMON_SUCCESS"])
        await play_voice(
            message=system_messages["SUMMON_SUCCESS"],
            server_id=server_id,
            discord_user_id=discord_user_id,
        )
    # 接続失敗
    else:
        await context.channel.send(system_messages["SUMMON_FAILURE"])
    return


@bot.command()
async def disconnect(context) -> None:
    global voice_clients

    # サーバIDを取得
    server_id: str = str(context.guild.id)
    # ボイスクライアント・テキストチャンネルを取得
    voice_client = voice_clients.get(server_id)

    # 切断
    if voice_client is not None:
        await context.channel.send(system_messages["BYE_SUCCESS"])
        await voice_client.disconnect()
        voice_clients[server_id] = None
        text_channels[server_id] = None
    else:
        await context.channel.send(system_messages["BYE_FAILURE"])

    return


@bot.command()
async def change(context, voice_name: str) -> None:
    discord_user_id: int = context.author.id
    display_name: str = context.author.display_name
    server_id: str = str(context.guild.id)

    # 該当する条件の声を取得
    voice_categories_filtered: List[TYPE_VOICE_CATEGORY] = [
        voice_category
        for voice_category in voice_categories
        if voice_category["name"] == voice_name
    ]
    # 声の取得に失敗
    if len(voice_categories_filtered) == 0:
        await context.channel.send(system_messages["CHANGE_FAILURE"])
        return

    # 声の取得に成功
    voice_category: TYPE_VOICE_CATEGORY = voice_categories_filtered[0]

    message: str = voice_category["message"].format(display_name)
    voice: str = voice_category["voice"]

    # ユーザをデータベースから検索
    user: TYPE_USER = sql_client.select_user(discord_user_id)

    # ユーザが存在しない場合
    if user is None:
        sql_client.insert_user(
            discord_user_id=discord_user_id, name=display_name, voice=voice
        )

    # ユーザが存在する場合
    else:
        sql_client.update_user(
            discord_user_id=discord_user_id, name=display_name, voice=voice
        )

    await context.channel.send(message)
    await play_voice(
        message=message,
        server_id=server_id,
        discord_user_id=discord_user_id,
    )

    return


@bot.listen()
async def on_message(context) -> None:
    # サーバIDを取得
    server_id: str = str(context.guild.id)
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
    user: TYPE_USER = sql_client.select_user(discord_user_id=discord_user_id)
    if user is None:
        voice = voice_categories[0]["voice"]
    elif user.get("voice") is None or not user.get("voice") in [
        voice_category["voice"] for voice_category in voice_categories
    ]:
        voice = voice_categories[0]["voice"]
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
    voice_client.play(
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

    return
