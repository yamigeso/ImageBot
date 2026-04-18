"""
netkeiba 画像表示 Discord BOT
================================

netkeibaのスマホ版から保存した画像は拡張子が付いていないため、
Discordで「ファイル」として扱われ、画像として表示されません。

このBOTは、拡張子なしで投稿された添付ファイルの中身を判定し、
画像であれば正しい拡張子を付けて自動的に再投稿します。
"""

import io
import os

import discord
from discord.ext import commands

from keep_alive import keep_alive


# 画像ファイルのマジックナンバー（ファイル先頭バイト列）と拡張子の対応表
IMAGE_SIGNATURES: list[tuple[bytes, str]] = [
    (b"\x89PNG\r\n\x1a\n", "png"),
    (b"\xff\xd8\xff", "jpg"),
    (b"GIF87a", "gif"),
    (b"GIF89a", "gif"),
    (b"BM", "bmp"),
    # WebP は "RIFF....WEBP" という構造なので別途判定
]


def detect_image_extension(data: bytes) -> str | None:
    """ファイルのバイトデータから画像の拡張子を判定する。

    画像でない場合は None を返す。
    """
    for signature, ext in IMAGE_SIGNATURES:
        if data.startswith(signature):
            return ext

    # WebP 判定（RIFF....WEBP）
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"

    return None


# Discord BOT の初期化
intents = discord.Intents.default()
intents.message_content = True  # メッセージ本文と添付ファイルを読むのに必要
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready() -> None:
    print(f"✅ BOTが起動しました: {bot.user}")
    print(f"   サーバー数: {len(bot.guilds)}")


@bot.event
async def on_message(message: discord.Message) -> None:
    # BOT自身のメッセージは無視（無限ループ防止）
    if message.author.bot:
        return

    # 添付ファイルがなければ何もしない
    if not message.attachments:
        await bot.process_commands(message)
        return

    fixed_files: list[discord.File] = []

    for attachment in message.attachments:
        filename = attachment.filename or "image"

        # すでに画像の拡張子が付いている場合はスキップ
        lower_name = filename.lower()
        if any(lower_name.endswith(f".{ext}") for ext in
               ("png", "jpg", "jpeg", "gif", "webp", "bmp")):
            continue

        # ファイルの先頭を読み込んで画像形式を判定
        try:
            data = await attachment.read()
        except Exception as e:
            print(f"⚠️  添付ファイル読み込みエラー: {e}")
            continue

        ext = detect_image_extension(data)
        if not ext:
            # 画像ではないのでスキップ
            continue

        new_filename = f"{filename}.{ext}"
        fixed_files.append(
            discord.File(io.BytesIO(data), filename=new_filename)
        )
        print(f"🖼️  画像を検出: {filename} → {new_filename}")

    # 修正対象がなければ終了
    if not fixed_files:
        await bot.process_commands(message)
        return

    # 拡張子を補正した画像を再投稿
    try:
        await message.channel.send(
            content=f"📷 {message.author.mention} さんの予想画像",
            files=fixed_files,
        )
        # 元のメッセージにリアクションを付けて「処理した」ことを示す
        try:
            await message.add_reaction("✅")
        except discord.Forbidden:
            pass
    except discord.Forbidden:
        print("⚠️  メッセージ送信権限がありません")
    except Exception as e:
        print(f"⚠️  送信エラー: {e}")

    await bot.process_commands(message)


@bot.command(name="ping")
async def ping(ctx: commands.Context) -> None:
    """BOTが動作しているか確認するコマンド。"""
    await ctx.send(f"🏇 pong! ({round(bot.latency * 1000)}ms)")


if __name__ == "__main__":
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "環境変数 DISCORD_BOT_TOKEN が設定されていません。"
            "Replit の Secrets に登録してください。"
        )

    keep_alive()  # Replit 用：常時起動のための Web サーバー
    bot.run(token)
