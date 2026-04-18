# netkeiba 画像表示 Discord BOT

netkeibaのスマホ版からダウンロードした「拡張子のない画像ファイル」を、Discordに投稿すると自動で画像として表示し直してくれるBOTです。

## なぜ必要？

netkeibaスマホ版で予想をダウンロードすると、ファイル名が `1776489612923` のように **拡張子なし** で保存されます。Discordは拡張子でファイル種類を判定するため、拡張子なしファイルは画像と認識されず「ファイル添付」として表示されてしまいます。

このBOTは、投稿されたファイルの先頭バイト（マジックナンバー）を見て画像形式（PNG/JPEG/GIF/WebP/BMP）を判定し、正しい拡張子を付けて再投稿します。

## 構成

```
.
├── main.py           # BOT本体
├── keep_alive.py     # Replit常時起動用のWebサーバー
├── requirements.txt  # 必要なPythonパッケージ
└── .replit           # Replitの実行設定
```

## セットアップ手順

### 1. Discord Developer PortalでBOTを作成

1. https://discord.com/developers/applications を開く
2. 右上「**New Application**」をクリックし、好きな名前を付ける（例: `netkeiba-image-bot`）
3. 左メニュー「**Bot**」を開き、「**Reset Token**」でトークンを発行しコピー（この文字列は後で使う）
4. 同じ画面を下にスクロールし、「**Privileged Gateway Intents**」セクションで以下をON：
   - ✅ **MESSAGE CONTENT INTENT**

### 2. BOTをサーバーに招待

1. 左メニュー「**OAuth2**」→「**URL Generator**」を開く
2. **SCOPES** で `bot` にチェック
3. **BOT PERMISSIONS** で以下にチェック：
   - ✅ View Channels
   - ✅ Send Messages
   - ✅ Attach Files
   - ✅ Read Message History
   - ✅ Add Reactions
4. 下に表示されたURLをブラウザで開き、BOTを自分のサーバーに招待

### 3. Replitにデプロイ

1. https://replit.com/ にログイン
2. 「**+ Create Repl**」→ テンプレート「**Python**」を選択
3. 作成したReplに、この4ファイル（`main.py`, `keep_alive.py`, `requirements.txt`, `.replit`）をアップロード
4. 左サイドバーの🔒「**Secrets**」を開き、以下を追加：
   - Key: `DISCORD_BOT_TOKEN`
   - Value: 手順1でコピーしたBOTのトークン
5. 上部「**Run**」ボタンで起動
6. 起動すると右上にWebビューが表示され、`Discord BOT is alive!` と出るURLが分かる（このURLを次で使う）

### 4. 常時起動の設定（UptimeRobot）

Replit無料プランは一定時間アクセスがないと停止するため、外部から定期的にpingを送る必要があります。

1. https://uptimerobot.com/ に無料登録
2. 「**Add New Monitor**」をクリック
3. 以下を設定：
   - Monitor Type: **HTTP(s)**
   - Friendly Name: `netkeiba-bot` など
   - URL: 手順3で確認したReplitのWebビューURL
   - Monitoring Interval: **5 minutes**
4. 保存すれば5分おきに自動でReplitにアクセスし、BOTが起動し続けます

## 使い方

設定が終わったら、Discordの任意のチャンネルにnetkeibaで保存した拡張子なし画像を投稿するだけ。BOTが自動で画像として再投稿し、元の投稿に✅のリアクションを付けます。

動作確認は `!ping` コマンドでもOK（`🏇 pong!` と返ってきます）。

## 技術メモ

- 画像判定はファイル先頭の **マジックナンバー** を見ています。netkeibaの画像は実質PNGなので `\x89PNG` シグネチャで検出します。
- 既に画像拡張子（.png/.jpg等）が付いたファイルはスキップするので、通常の画像投稿には影響しません。
- BOTは元メッセージを削除しません。気になる場合は `main.py` の `add_reaction` 部分に `await message.delete()` を追加してください（BOTに「メッセージの管理」権限が必要）。

## トラブルシューティング

**BOTがオンラインにならない**
Replitで`Run`を押した後、コンソールに `✅ BOTが起動しました` と出るか確認。出ていなければトークンが正しく登録されているか、`MESSAGE CONTENT INTENT` がONになっているかを再確認してください。

**画像が再投稿されない**
BOTに「ファイル添付」「メッセージ送信」権限が付いているか、対象チャンネルの権限も確認してください。

**数時間経つと止まる**
UptimeRobotのMonitorが本当にReplitのURLを叩けているか（Monitor詳細でResponse Timeが記録されているか）を確認してください。
