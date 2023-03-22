import asyncio
import re
from typing import Dict, List, Optional

import discord
from discord import TextChannel, VoiceClient
from discord.ext import commands

from abstracts import AbstractSqlClient, AbstractVoiceGenerator
from commons import (
    TYPE_DICTIONARY,
    TYPE_SYSTEM_MESSAGES,
    TYPE_USER,
    TYPE_VOICE_CATEGORY,
)

# ボットの定義
intents = discord.Intents.all()
bot = commands.Bot(intents=intents)
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
# 適用サーバ一覧
guild_ids: List[str]


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
    server_id = str(member.guild.id)
    # 入退室者の名前の取得
    name = member.display_name
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
                discord_user_id=None,
            )

        # メンバーの退出時
        if after.channel is None:
            message = system_messages["FAREWELL"].format(name)
            await text_channel.send(message)
            await play_voice(
                message=message,
                server_id=server_id,
                discord_user_id=None,
            )

        # 誰も居なくなった時に自動で退出
        if len(voice_client.channel.voice_states.keys()) == 1:  # type: ignore
            await voice_client.disconnect()
            voice_clients[server_id] = None
            text_channels[server_id] = None

    return


@bot.slash_command(guild_ids=guild_ids)
async def connect(context) -> None:
    global voice_clients

    # サーバIDを取得
    server_id: str = str(context.guild.id)

    # 呼び出したユーザの参加しているボイスチャンネルを取得
    target_voice_channel = context.author.voice
    # 接続成功
    if target_voice_channel is not None:
        voice_clients[server_id] = await target_voice_channel.channel.connect()
        text_channels[server_id] = context.channel
        await context.respond(system_messages["SUMMON_SUCCESS"])
        await play_voice(
            message=system_messages["SUMMON_SUCCESS"],
            server_id=server_id,
            discord_user_id=None,
        )
    # 接続失敗
    else:
        await context.respond(system_messages["SUMMON_FAILURE"])
    return 


@bot.slash_command(guild_ids=guild_ids)
async def disconnect(context) -> None:
    global voice_clients

    # サーバIDを取得
    server_id: str = str(context.guild.id)
    # ボイスクライアント・テキストチャンネルを取得
    voice_client = voice_clients.get(server_id)

    # 切断
    if voice_client is not None:
        await context.respond(system_messages["BYE_SUCCESS"])
        await voice_client.disconnect()
        voice_clients[server_id] = None
        text_channels[server_id] = None
    else:
        await context.respond(system_messages["BYE_FAILURE"])

    return


@bot.slash_command(guild_ids=guild_ids)
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
        await context.respond(system_messages["CHANGE_FAILURE"])
        return

    # 声の取得に成功
    voice_category: TYPE_VOICE_CATEGORY = voice_categories_filtered[0]
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

    message: str = voice_category["message"].format(display_name)
    await context.respond(message)
    await play_voice(
        message=message,
        server_id=server_id,
        discord_user_id=discord_user_id,
    )

    return


@bot.slash_command(guild_ids=guild_ids)
async def dictionary(context, word: str, reading: str) -> None:
    server_id: str = str(context.guild.id)

    # 単語辞書をデータベースから検索
    target_dictionary = sql_client.select_dictionary(
        discord_server_id=server_id, word=word
    )

    # 単語辞書が存在しない場合
    if target_dictionary is None:
        sql_client.insert_dictionary(
            discord_server_id=server_id, word=word, reading=reading
        )

    # 単語辞書が存在する場合
    else:
        sql_client.update_dictionary(
            discord_server_id=server_id, word=word, reading=reading
        )

    message: str = system_messages["DICTIONARY_SUCCESS"].format(word, reading)
    await context.respond(message)
    await play_voice(
        message=message,
        server_id=server_id,
        discord_user_id=None,
    )

    return


@bot.slash_command(guild_ids=guild_ids)
async def delete_dictionary(context, word: str) -> None:
    server_id: str = str(context.guild.id)

    target_dictionary = sql_client.select_dictionary(
        discord_server_id=server_id, word=word
    )

    # 単語辞書が存在しない場合
    if target_dictionary is None:
        message = system_messages["DELETE_DICTIONARY_FAILURE"].format(word)
        await context.respond(message)
        await play_voice(
            message=message,
            server_id=server_id,
            discord_user_id=None,
        )
        return

    # 単語辞書が存在する場合
    sql_client.delete_dictionary(discord_server_id=server_id, word=word)

    message = system_messages["DELETE_DICTIONARY_SUCCESS"].format(word)
    await context.respond(message)
    await play_voice(
        message=message,
        server_id=server_id,
        discord_user_id=None,
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
        or context.content.startswith("/")
        or text_channel.id != context.channel.id
    ):
        return

    dictionaries: List[TYPE_DICTIONARY] = sql_client.select_dictionaries(
        discord_server_id=server_id
    )

    message = replace_dictionaries(
        message=context.content, dictionaries=dictionaries
    )
    await play_voice(
        message=message, server_id=server_id, discord_user_id=discord_user_id
    )

    return


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
    # ボイスチャンネルを取得
    voice_client = voice_clients.get(server_id)
    # ボイスチャンネルが未定義のとき無視
    if voice_client is None:
        return

    # 再生するボイスを設定
    voice = get_voice(discord_user_id=discord_user_id)

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


def get_voice(discord_user_id: Optional[int]) -> str:
    # 再生する声の取得
    if discord_user_id is None:
        # デフォルトで再生
        voice = voice_categories[0]["voice"]
    else:
        # クエリを実行
        user: TYPE_USER = sql_client.select_user(
            discord_user_id=discord_user_id
        )
        # ユーザのボイスが未登録のとき、デフォルトで再生
        if user is None:
            voice = voice_categories[0]["voice"]
        # ユーザに登録可能なボイス以外のボイスが登録されていたとき / 別の音声生成器で登録されたもの
        elif not user.get("voice") in [
            voice_category["voice"] for voice_category in voice_categories
        ]:
            voice = voice_categories[0]["voice"]
        # ユーザの登録ボイスが取得できたとき
        else:
            voice = user["voice"]
    return voice


def run(
    token: str,
    guild_ids_: List[str],
    voice_generator_: AbstractVoiceGenerator,
    sql_client_: AbstractSqlClient,
    sound_file_path_: str,
) -> None:
    global voice_generator
    global voice_categories
    global system_messages
    global sql_client
    global sound_file_path
    global guild_ids

    voice_generator = voice_generator_
    voice_categories = voice_generator.get_voice_categories()
    system_messages = voice_generator.get_system_messages()
    sql_client = sql_client_
    sound_file_path = sound_file_path_
    guild_ids = guild_ids_

    bot.run(token)

    return
